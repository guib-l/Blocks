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







class InterfaceErrorType(str, Enum):
    INPUT = "Wrong input"
    OUTPUT = "Wrong output"
    ERROR = "Error in message"
    TIMEOUT = "Timeout error"
    CONNECTION = "Connection error"
    VALIDATION = "Validation error"
    SERIALIZATION = "Serialization error"
    SECURITY = "Security error"
    PERMISSION = "Permission denied"




class InterfaceError(Exception):

    err_type = None

    def __init__(self, 
                 message: str = "Protocole error occurred", 
                 err_type: Optional[str] = None):
        
        self._set_error_type(err_type)

        if err_type is not None:
            message = f"{message}: Error Protocole : '{self.err_type}'"
        else:
            message = f"{message}: Error Protocole unknow"

        super().__init__(message)

    def _set_error_type(self, value):

        if value in [s.name for s in InterfaceErrorType]:
            self.err_type = InterfaceErrorType[value]

    def to_dict(self):
        """Convertit l'erreur en dictionnaire pour la sérialisation."""
        return {
            "type": self.err_type.name if self.err_type else "UNKNOWN",
            "message": str(self),
            "details": self.details
        }




class Interface:
        
    # Installer un nombre limite de message en mémoire
    # Si persistant est True, les messages ne sont pas supprimés après envoi
    # et restent disponibles pour consultation
    # Si persistant est False, les messages sont supprimés après envoi
    # et ne sont pas disponibles pour consultation


    def __init__(self, 
                 object: Any = None,
                 persistant: bool = False,
                 restricted: bool = False,
                 lim_inp: tuple = (99,99),
                 lim_out: tuple = (99,99),):

        self.object = object
        # Delete input/output when output is asked
        self.persistant = persistant # (Not implemented)

        # Cannot deliver output if loower input limits and
        # lower output limit didn't reach.
        self.restricted = restricted # (Not implemented)

        self._limits_inp = lim_inp
        self._limits_out = lim_out

        # Initialize message storage
        self.__REGISTER__ = {}  
        self.__OUTPUTS__  = {}   
        self.__ERROR__    = MESSAGE()
            
        # Current active message (for compatibility)
        self.__ACTIVE_REGISTER__ = MESSAGE()
        self.__ACTIVE_OUTPUT__   = MESSAGE()

        
    
    @property
    def id(self) -> str:
        """Return the ID of the associated object or a generated ID if none exists."""
        return getattr(self.object, 'id', str(uuid.uuid4()))

    # -----------------------------------------------------
    # Serialization methods
    # A revoir

    def to_dict(self) -> Dict[str, Any]:
        return {
            'interface_of': self.id,
            'persistant': self.persistant,
            'lim_inp':self._limits_inp,
            'lim_out':self._limits_out,
        }

    @classmethod
    def from_dict(cls, ) -> None:
        return cls

    #-----------------------------------------------------
    # Interface methods

    def provide(self, key: str, value: Any, output_index: int = -1) -> None:
        """
        Store a value in the output message data dictionary.
        
        Args:
            key: The key to store the value under
            value: The value to store
            output_index: The index of the output to modify (-1 for the active output)
        """
        if output_index == -1:
            # Modify active output
            if not hasattr(self.__ACTIVE_OUTPUT__, 'DATA') or not isinstance(self.__ACTIVE_OUTPUT__.DATA, dict):
                self.__ACTIVE_OUTPUT__.DATA = {}
            self.__ACTIVE_OUTPUT__.DATA[key] = value
        else:
            # Modify specific output in the list
            if output_index >= len(self.__OUTPUTS__):
                # Create new outputs until we reach the desired index
                for _ in range(len(self.__OUTPUTS__), output_index + 1):
                    self.__OUTPUTS__.update({_:deepcopy(MESSAGE())})

            if not hasattr(self.__OUTPUTS__[output_index], 'DATA') or not isinstance(self.__OUTPUTS__[output_index].DATA, dict):
                self.__OUTPUTS__[output_index].DATA = {}
            self.__OUTPUTS__[output_index].DATA[key] = value

    def merge(self, 
              key: str = None, 
              output: bool = True) -> dict:
        """
        Merge data from all registered messages or outputs under a specific key. 
        Args:
            key: The key to merge data from
            output: If True, merge from outputs; if False, merge from registered inputs
        Returns:
            A dictionary containing merged data
        """
        merged_data = {}
        source = self.__OUTPUTS__ if output else self.__REGISTER__
        for idx, msg in source.items():
            if isinstance(msg, MESSAGE) and isinstance(msg.DATA, dict) and key in msg.DATA:
                merged_data.update( msg.DATA[key] )
            else:
                merged_data.update( msg.DATA )
        return merged_data


    def receive(self, 
                message: Union[MESSAGE, List[MESSAGE]],
                index:int = -1) -> Union[MESSAGE, List[MESSAGE]]:
        """
        Process incoming message(s) and store in the register.
        
        Args:
            message: A single MESSAGE or a list of MESSAGEs
            
        Returns:
            The processed message(s)
        """
        # Handle single message case
        if isinstance(message, MESSAGE):
            return self._receive_single(message, index=index)
        
        # Handle multiple messages
        if isinstance(message, list):
            results = {}
            for idx,msg in enumerate(message):
                results.update({idx:self._receive_single(msg)})
            return results
            
        raise InterfaceError("Invalid message format", "VALIDATION")
    
    def _receive_single(self, message: MESSAGE, index:int=-1) -> MESSAGE:
        """Process a single incoming message."""
        if not isinstance(message, MESSAGE):
            raise InterfaceError("Invalid message format", "VALIDATION")
            
        # Set received timestamp
        message.DATE_RECEIVED = datetime.now()
        
        # Verify message destination
        if message.TO and message.TO != self.id:
            raise InterfaceError("Le message n'est pas destiné à ce block", "PERMISSION")
        
        # Store message in register
        if index == -1:
            index = len(self.__REGISTER__) + 1

            # If reach limits then ignore messages above
            if index>self._limits_inp[1]:
                return message
            
        self.__REGISTER__.update({index : message})
        self.__ACTIVE_REGISTER__ = message
        
        return message

    def send(self, message: Optional[Union[MESSAGE, List[MESSAGE]]] = None) -> Union[MESSAGE, List[MESSAGE]]:
        """
        Send message(s).
        
        Args:
            message: Optional message or list of messages to send
            
        Returns:
            The sent message(s)
        """
        if message is not None:
            if isinstance(message, MESSAGE):
                self.__ACTIVE_OUTPUT__ = message
                self.__OUTPUTS__ = {0:message}
            elif isinstance(message, list):
                self.__OUTPUTS__ = {idx:msg for idx,msg in enumerate(message) if idx<self._limits_out[1]}
                if message:
                    self.__ACTIVE_OUTPUT__ = message[-1]
        
        # If we have no outputs, use the active output
        if not self.__OUTPUTS__:
            self.__OUTPUTS__ = {0:self.__ACTIVE_OUTPUT__}
            
        # Process all outputs
        for i,(_,output) in enumerate(self.__OUTPUTS__.items()):
            if not isinstance(output, MESSAGE):
                raise InterfaceError(f"Invalid output message at index {i}", "VALIDATION")
            
            # Set sender and timestamp if not already set
            if not output.FROM:
                output.FROM = self.id
            if not output.DATE_SEND:
                output.DATE_SEND = datetime.now()
        
        # Return all outputs or just the active output if there's only one
        if len(self.__OUTPUTS__) == 1:
            return self.__OUTPUTS__[0]
        return self.__OUTPUTS__
        
    def clear_register(self) -> None:
        """Clear the message register."""
        self.__REGISTER__ = {}
        self.__ACTIVE_REGISTER__ = MESSAGE()
        
    def clear_outputs(self) -> None:
        """Clear the output messages."""
        self.__OUTPUTS__ = {}
        self.__ACTIVE_OUTPUT__ = MESSAGE()

    # -----------------------------------------------------
    # Interface dataset

    @property
    def error(self) -> MESSAGE: 
        return self.__ERROR__

    @error.setter
    def error(self, err: MESSAGE) -> None: 
        if not isinstance(err, MESSAGE):
            raise ValueError("Error must be a MESSAGE object")
        self.__ERROR__ = deepcopy(self.__ACTIVE_REGISTER__)
        self.__ERROR__.ERROR = err
        self.__ERROR__.FROM = self.id
        self.__ERROR__.DATE_SEND = datetime.now()

    @property
    def input(self) -> Union[MESSAGE, List[MESSAGE]]: 
        """Get the current input message(s)."""
        if len(self.__REGISTER__) <= 1:
            return self.__ACTIVE_REGISTER__
        return self.__REGISTER__

    @input.setter
    def input(self, inp: Union[MESSAGE, List[MESSAGE]]) -> None: 
        """Set the input message(s)."""
        if isinstance(inp, MESSAGE):
            self._set_single_input(inp)
        elif isinstance(inp, list) and all(isinstance(msg, MESSAGE) for msg in inp):
            self.__REGISTER__ = {}
            for msg in inp:
                self._set_single_input(msg)
        else:
            raise ValueError("Input must be a MESSAGE object or list of MESSAGE objects")

    def _set_single_input(self, inp: MESSAGE, index:int=-1) -> None:
        """Helper to set a single input message."""
        if not isinstance(inp, MESSAGE):
            raise ValueError("Input must be a MESSAGE object")

        inp.DATE_RECEIVED = datetime.now()

        if inp.TO == self.id or inp.TO is None:
            if index == -1:index = len(self.__REGISTER__)+1

            if index>=self._limits_inp[1]:
                return 
            
            self.__REGISTER__.update({index:inp})
            self.__ACTIVE_REGISTER__ = inp
        else:
            raise InterfaceError("Le message n'est pas destiné à ce block", "PERMISSION")

    @property
    def output(self) -> Union[MESSAGE, List[MESSAGE]]: 
        """Get the current output message(s)."""
        if not self.__OUTPUTS__:
            # Create output from current register if no outputs exist
            self.__ACTIVE_OUTPUT__ = deepcopy(self.__ACTIVE_REGISTER__)
            self.__ACTIVE_OUTPUT__.FROM = self.id
            self.__ACTIVE_OUTPUT__.DATE_SEND = datetime.now()
            self.__OUTPUTS__ = {0:self.__ACTIVE_OUTPUT__}
            
        if self.restricted:
            self.clear_register()

        if len(self.__OUTPUTS__) == 1:
            return self.__OUTPUTS__[0]
        
        return self.__OUTPUTS__

    @output.setter
    def output(self, out: Union[MESSAGE, List[MESSAGE]]) -> None: 
        """Set the output message(s)."""
        if isinstance(out, MESSAGE):
            if not isinstance(out, MESSAGE):
                raise ValueError("Output must be a MESSAGE object")
            self.__ACTIVE_OUTPUT__ = out
            self.__OUTPUTS__ = {0:out}
        elif isinstance(out, list) and all(isinstance(msg, MESSAGE) for msg in out):
            self.__OUTPUTS__ = {idx:_out for idx,_out in enumerate(out) if idx<self._limits_out[1]}

            if out:
                self.__ACTIVE_OUTPUT__ = out[-1]
        else:
            raise ValueError("Output must be a MESSAGE object or list of MESSAGE objects")

    @property
    def register(self) -> List[MESSAGE]:
        """Get all registered input messages."""
        return self.__REGISTER__
        
    @property
    def outputs(self) -> List[MESSAGE]:
        """Get all output messages."""

        if self.restricted:
            self.clear_register()

        return self.__OUTPUTS__
    





