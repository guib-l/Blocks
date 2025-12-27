import os
import sys
import io
import uuid
import zipfile
import json
import asyncio
import threading
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



from queue import Queue


def get_new_label(exist_label:Any, new_label:Any=None) -> str:
    """Génère un label unique si aucun n'est fourni."""
    
    if exist_label is None:
        return 0
    
    if new_label is None:
        incr = 0
        while label in exist_label:
            label = len(exist_label)-1 + incr
            incr += 1
        return label
        
    

class DataQueue:
    """File de messages simple."""
    def __init__(self):
        self._queue:List[Any] = []
        self._index:List[Any] = []
        self._lock = threading.Lock()

    def put(self, message:Any, label=None) -> None:
        """Ajoute un message à la file."""
        print(f"Putting message with label {label}: {message}") 
        with self._lock:
            self._queue.append(message)
            if label is None or label in self._index:
                label = get_new_label(self._index, label)
            self._index.append(label)

    def get(self, label=None) -> Optional[Any]:
        """Récupère le premier message de la file."""
        with self._lock:
            if label is None:
                if self._queue:
                    self._index.pop(0)
                    return self._queue.pop(0)
                return None
            
            for i, msg_label in enumerate(self._index):
                if msg_label == label:
                    self._index.pop(i)
                    return self._queue.pop(i)
        return None
    
    def dequeue_by_label(self, label:Any) -> Optional[Any]:
        """Récupère un message de la file par son label."""
        with self._lock:
            for i, msg_label in enumerate(self._index):
                if msg_label == label:
                    self._index.pop(i)
                    return self._queue.pop(i)
        return None
    
    def empty(self) -> None:
        """Vide la file de messages."""
        with self._lock:
            self._queue.clear()
            self._index.clear()

    def not_empty(self) -> bool:
        """Vérifie si la file est vide."""
        with self._lock:
            return len(self._queue) != 0
        
    def __repr__(self):
        return f"DataQueue(num_messages={len(self._queue)})"




class DataPacketQueue:
    """File de messages avec support de priorité.

    TODO: gérer les priorités dans la file ?? (est-ce utile ?)
    """
    def __init__(self):
        self._queues: List[DataPacket] = []
        self._lock = threading.Lock()

    def enqueue(self, message:DataPacket) -> None:
        """Ajoute un message à la file."""
        with self._lock:
            self._queues.append(message)

    def dequeue(self) -> Optional[DataPacket]:
        """Récupère le premier message de la file."""
        with self._lock:
            if self._queues:
                return self._queues.pop(0)
        return None
    
    def dequeue_by_property(self, 
                            all_results=True,
                            **filters) -> Optional[DataPacket]:
        """
        Récupère Tout les messages correspondant aux propriétés spécifiées.
        """
        _all_msg = []

        with self._lock:
            for i, message in enumerate(self._queues):
                if all(getattr(message, key, None) == value for key, value in filters.items()):
                    if not all_results:
                        return self._queues.pop(i)
                    else:
                        _all_msg.append(message)
                        
        if all_results:
            for msg in _all_msg:
                self._queues.remove(msg)
            return _all_msg
        return None
    
    def peek_by_property(self, 
                         all_results=True, 
                         **filters) -> Optional[DataPacket]:
        """
        Consulte tout les messages correspondant aux propriétés sans les retirer.
        """
        _all_msg = []

        with self._lock:
            for message in self._queues:
                if all(getattr(message, key, None) == value for key, value in filters.items()):
                    if not all_results:
                        return message
                    else:
                        _all_msg.append(message)
        if all_results:
            return _all_msg
        
        return None

    def empty(self) -> None:
        """Vide la file de messages."""
        with self._lock:
            self._queues.clear()
    
    def is_empty(self) -> bool:
        """Vérifie si la file est vide."""
        with self._lock:
            return all(len(q) == 0 for q in self._queues.values())

    def __repr__(self):
        return f"DataPacketQueue(num_messages={len(self._queues)})"





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





























