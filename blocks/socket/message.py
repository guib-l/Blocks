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

MESSAGE = TypeVar('MESSAGE', bound='MESSAGE')


class MessageType(str, Enum):
    """Types de messages supportés par le protocole."""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"
    ERROR = "error"
    INFO = "information"
    DIRECT = "direct"


class MessagePriority(int, Enum):
    """Priorités possibles pour les messages."""
    LOW = 0
    NORMAL = 1
    HIGH = 2
    URGENT = 3

class MESSAGE(DataSet):    

    def __init__(self, 
                 FROM: Optional[str] = None,
                 TO: Optional[str] = None,
                 TYPE: Optional[str] = MessageType.DIRECT,
                 SUBJECT: Optional[str] = None,
                 PRIORITY: int = MessagePriority.NORMAL,
                 DELAY: Optional[float] = None,
                 TRANSFORM: Optional[Callable] = None,
                 DATE_RECEIVED: Optional[datetime] = None,
                 EXPIRY: Optional[datetime] = None,
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
        return ("MESSAGE(\n" +
                f"  FROM = {self.FROM} \n" + 
                f"  TO   = {self.TO} \n" + 
                f"  RECEIVED = {self.DATE_RECEIVED} \n" + 
                f"  SEND     = {self.DATE_SEND} \n" + 
                f"  DATA_KEYS={list(self.DATA.keys() if isinstance(self.DATA, dict) else [])}\n"+
                ")")
    
    @classmethod
    def generate_response(cls, 
                          object: Any,
                          to: str = None,
                          data: Dict[str, Any]={},
                          **kwargs) -> MESSAGE:
        return cls(
            FROM=object.id,
            TO=to,
            TYPE=MessageType.RESPONSE,
            DATA=data,
            **kwargs)

    @classmethod
    def generate_request(cls, 
                         object: Any,
                         to: str,
                         subject: str,
                         data: Dict[str, Any],
                         priority: int = MessagePriority.NORMAL,
                         delay: Optional[float] = None,
                         transform: Optional[Callable] = None,
                         async_mode: bool = False,
                         expiry: Optional[datetime] = None,
                         metadata: Optional[Dict[str, Any]] = None,
                         **kwargs) -> MESSAGE:
        return cls(
            FROM=object.id,
            TO=to,
            TYPE=MessageType.REQUEST,
            SUBJECT=subject,
            PRIORITY=priority,
            DELAY=delay,
            TRANSFORM=transform,
            ASYNC=async_mode,
            EXPIRY=expiry,
            METADATA=metadata,
            DATA=data,
            **kwargs)

    @classmethod
    def generate_event(cls, 
                       subject: str,
                       data: Dict[str, Any],
                       priority: int = MessagePriority.NORMAL,
                       metadata: Optional[Dict[str, Any]] = None,
                       **kwargs) -> MESSAGE:   
        return cls(
            FROM=object.id,
            TYPE=MessageType.EVENT,
            SUBJECT=subject,
            PRIORITY=priority,
            METADATA=metadata,
            DATA=data,
            **kwargs )
    
    @classmethod
    def generate_info(cls,
                       object: Any,
                       subject: Optional[str] = None,
                       priority: int = MessagePriority.HIGH,
                       info:str = None):
        return cls(
            FROM=object.id,
            TYPE=MessageType.INFO,
            SUBJECT="Information",
            PRIORITY=priority,
            DATA={'info':info})

    @classmethod
    def generate_error(cls,
                       object: Any, 
                       to: str,
                       error_info: Dict[str, Any],
                       subject: Optional[str] = None,
                       priority: int = MessagePriority.HIGH,
                       metadata: Optional[Dict[str, Any]] = None,) -> MESSAGE:
        return cls(
            FROM=object.id,
            TO=to,
            TYPE=MessageType.ERROR,
            SUBJECT=subject,
            PRIORITY=priority,
            METADATA=metadata,
            ERROR=error_info,)



