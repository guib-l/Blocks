import json
from datetime import *
from copy import copy, deepcopy
import csv
from typing import *
from abc import *
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable, Iterator, BinaryIO, TextIO

from blocks.base.dataset import DataSet

from enum import Enum




DataPacket = TypeVar('DataPacket', bound='DataPacket')


class DataPacketType(str, Enum):
    """Types de messages supportés par le protocole."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    INFO = "information"
    DIRECT = "direct"

class DataPacketPriority(int, Enum):
    """Priorités possibles pour les messages."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

class DataPacketStatus(str, Enum):
    """Statuts possibles d'un message."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    PROCESSED = "processed"
    FAILED = "failed"
    EXPIRED = "expired"



class DataPacket(DataSet):

    _authorize_keys = ['FROM', 'TO', 'TYPE', 'SUBJECT', 
                       'PRIORITY', 'DELAY', 'TRANSFORM', 
                       'ASYNC', 'DATE_RECEIVED', 'DATE_SEND', 
                       'EXPIRY', 'METADATA', 'DATA', 'ERROR']
    
    def __new__(cls,**kwargs):

        for key,_ in kwargs.items():
            if key not in cls._authorize_keys:
                raise TypeError(f'Key {key} not authorized.')
            
        return super().__new__(cls)

    def __init__(self, 
                 FROM: Optional[str] = None,
                 TO: Optional[str] = None,
                 TYPE: Optional[str] = DataPacketType.DIRECT,
                 SUBJECT: Optional[str] = None,
                 PRIORITY: int = DataPacketPriority.NORMAL,
                 DELAY: Optional[float] = 0.0,
                 TRANSFORM: Optional[Callable] = None,
                 DATE_RECEIVED: Optional[datetime] = datetime.now(),
                 EXPIRY: Optional[datetime] = float('inf'),
                 DATE_SEND: Optional[datetime] = None,
                 ASYNC: bool = False,
                 ERROR: Optional[Dict[str, Any]] = None,
                 DATA: Dict[str, Any] = {},
                 METADATA : Dict[str, Any] = None):
        
        super().__init__(FROM=FROM,
                         TO=TO,
                         TYPE=TYPE,
                         SUBJECT=SUBJECT,
                         PRIORITY=PRIORITY,
                         DELAY=DELAY,
                         TRANSFORM=TRANSFORM,
                         ASYNC=ASYNC,
                         DATE_RECEIVED=DATE_RECEIVED,
                         DATE_SEND=DATE_SEND,
                         EXPIRY=EXPIRY,
                         METADATA=METADATA,
                         DATA=DATA,
                         ERROR=ERROR)
        
    @property
    def is_expired(self) -> bool:
        """Vérifie si le message a expiré."""
        if self.EXPIRY:
            return datetime.now() > self.EXPIRY
        return False
    
    @property
    def has_error(self) -> bool:
        """Check if the message contains an error."""
        return self.ERROR is not None
    
    @property
    def transmission_time(self) -> Optional[float]:
        """Calculate the transmission time in seconds if both dates are available."""
        if self.DATE_RECEIVED and self.DATE_SEND:
            return (self.DATE_RECEIVED - self.DATE_SEND).total_seconds()
        return None
    
    
    def validate(self) -> bool:
        """Validate that the message has the required fields."""
        return self.FROM is not None and self.TO is not None
    
    def __repr__(self) -> str:
        """More concise representation focusing on key information."""
        return ("DataPacket(\n" +
                f"  FROM = {self.FROM} \n" + 
                f"  TO   = {self.TO} \n" + 
                f"  RECEIVED = {self.DATE_RECEIVED} \n" + 
                f"  SEND     = {self.DATE_SEND} \n" + 
                f"  TYPE={self.TYPE} \n" +
                f"  SUBJECT={self.SUBJECT} \n" +
                f"  PRIORITY={self.PRIORITY} \n" +
                f"  DELAY={self.DELAY} \n" +
                f"  ASYNC={self.ASYNC} \n" +
                f"  ERROR={self.ERROR} \n" +    
                f"  DATA_KEYS={list(self.DATA.keys() if isinstance(self.DATA, dict) else [])}\n"+
                ")")

                
    
    @classmethod
    def generate_message(cls, 
                         FROM: Any=None,
                         TO: str = None,
                         DATA: Dict[str, Any]={},
                         TYPE: str = DataPacketType.DIRECT,
                         **kwargs) -> 'DataPacket':
        return cls(
            FROM=FROM,
            TO=TO,
            TYPE=TYPE,
            DATA=DATA,
            **kwargs)

    @classmethod
    def generate_error(cls,
                       FROM: Any,
                       error: Any,
                       **kwargs):
        
        return cls(
            FROM=FROM,
            TO=None,
            ERROR=error,
            TYPE=DataPacketType.ERROR,
            **kwargs,
        )

    def to_dict(self) -> Dict[str, Any]:
        """Sérialise le message en dictionnaire."""
        return {
            'FROM': self.FROM,
            'TO': self.TO,
            'TYPE': self.TYPE.value,
            'SUBJECT': self.SUBJECT,
            'PRIORITY': self.PRIORITY,
            'DELAY': self.DELAY,
            'DATE_RECEIVED': self.DATE_RECEIVED.isoformat() if self.DATE_RECEIVED else None,
            'DATE_SEND': self.DATE_SEND.isoformat() if self.DATE_SEND else None,
            'EXPIRY': self.EXPIRY.isoformat() if self.EXPIRY else None,
            'ASYNC': self.ASYNC,
            'ERROR': self.ERROR,
            'DATA': self.DATA,
            'METADATA': self.METADATA
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> DataPacket:
        """Désérialise un dictionnaire en message."""
        # Convert ISO format strings back to datetime objects
        if data.get('DATE_RECEIVED'):
            data['DATE_RECEIVED'] = datetime.fromisoformat(data['DATE_RECEIVED'])
        if data.get('DATE_SEND'):
            data['DATE_SEND'] = datetime.fromisoformat(data['DATE_SEND'])
        if data.get('EXPIRY'):
            data['EXPIRY'] = datetime.fromisoformat(data['EXPIRY'])
        
        return cls(**data)
    
    def to_json(self) -> str:
        """Sérialise le message en JSON."""
        return json.dumps(self.to_dict(), indent=2)
    
    @classmethod
    def from_json(cls, json_str: str) -> DataPacket:
        """Désérialise un JSON en message."""
        data = json.loads(json_str)
        return cls.from_dict(data)

    def merge_data(self, 
                   other: Dict,
                   ignore_conflict=False,
                   ignore_keys: List[str]=[]) -> 'DataPacket':
        """Merge DATA from another DataPacket into this one."""
        merged_data = deepcopy(self.DATA)
        
        if isinstance(other, dict):
            for key, value in other.items():
                if key not in merged_data and key not in ignore_keys:
                    merged_data[key] = value
                else:
                    if not ignore_conflict:
                        raise KeyError(f"Key conflict during merge: {key}")
                    
                    if key not in ignore_keys:
                        # Overwrite existing key
                        merged_data[key] = value   
        
        return merged_data





























