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

from blocks.interface.message import MESSAGE,MessageType



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

def Exchange(args1, args2):
        
    def communicate(cls):

        cls.decorateur_args1 = args1
        cls.decorateur_args2 = args2

        class InterfaceMixin(cls):

            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)
                self._exchange_args1 = args1
                self._exchange_args2 = args2
        
        return InterfaceMixin
    
    return communicate



class Interface:
        
    # Installer un nombre limite de message en mémoire
    # Si persistant est True, les messages ne sont pas supprimés après envoi
    # et restent disponibles pour consultation
    # Si persistant est False, les messages sont supprimés après envoi
    # et ne sont pas disponibles pour consultation
    __ntype__ = 'interface'

    def __init__(self, 
                 node: Any = None,
                 persistant: bool = False,
                 restricted: bool = False,
                 max_inp: int = 999,
                 max_out: int = 999,
                 executor   = None,
                 environment = None, ):

        self.object = node
        # Delete input/output when output is asked
        self.persistant = persistant # (Not implemented)

        # Cannot deliver output if loower input limits and
        # lower output limit didn't reach.
        self.restricted = restricted # (Not implemented)

        self._limits_inp = max_inp
        self._limits_out = max_out

        # Initialize message storage
        self.__REGISTER__ = {}  
        self.__OUTPUTS__  = {}   
        self.__ERROR__    = MESSAGE()
            
        # Current active message (for compatibility)
        self.__ACTIVE_REGISTER__ = MESSAGE()
        self.__ACTIVE_OUTPUT__   = MESSAGE()

        self._executor = executor
        self._environment = environment

    # -----------------------------------------------------
    # Execution methods
    
    def execute(self, **data) -> Union[MESSAGE, List[MESSAGE]]:

        if hasattr(self.object, 'forward') and callable(getattr(self.object, 'forward')):
            result = self.object.forward(**data)
            if isinstance(result, MESSAGE) or (isinstance(result, list) and all(isinstance(msg, MESSAGE) for msg in result)):
                return result
            else:
                raise InterfaceError("L'exécution n'a pas retourné un message valide", "OUTPUT")
        else:
            raise InterfaceError("L'objet associé n'a pas de méthode 'forward' exécutable", "EXECUTION")
    


    # -----------------------------------------------------
    # Identification methods

    @property
    def id(self) -> str:
        """Return the ID of the associated object or a generated ID if none exists."""
        return getattr(self.object, 'id', str(uuid.uuid4()))

    # -----------------------------------------------------
    # Serialization methods

    def to_dict(self, 
                include_messages: bool = False) -> Dict[str, Any]:

        result = {
            'interface': self.__ntype__,
            'interface_of': getattr(self.object, '__ntype__', None) if self.object else None,
            'persistant': self.persistant,
            'restricted': self.restricted,
            'max_inp': self._limits_inp,
            'max_out': self._limits_out,
        }
        
        if include_messages:
            result['register'] = {idx: msg.to_dict() for idx, msg in self.__REGISTER__.items()}
            result['outputs'] = {idx: msg.to_dict() for idx, msg in self.__OUTPUTS__.items()}
        
        return result

    @classmethod
    def from_dict(cls, 
                  **data: Dict[str, Any]) -> 'Interface':
        kwargs = {
            'persistant': data.get('persistant', False),
            'restricted': data.get('restricted', False),
            'max_inp': data.get('max_inp', 999),
            'max_out': data.get('max_out', 999),
        }
        return cls(**kwargs)

    def to_json(self, include_messages: bool = False) -> str:
        return json.dumps(
            self.to_dict(include_messages=include_messages))
    
    def __str__(self) -> str:
        obj_type = getattr(self.object, '__ntype__', 'None') if self.object else 'None'
        return f"Interface(type={obj_type}, inputs={len(self.__REGISTER__)}, outputs={len(self.__OUTPUTS__)})"
    
    def __repr__(self) -> str:
        return f"Interface(id={self.id}, persistant={self.persistant}, restricted={self.restricted})"

    #-----------------------------------------------------
    # Interface methods

    def provide(self, 
                key: str, 
                value: Any, 
                output_index: int = -1) -> None:
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
                for i in range(len(self.__OUTPUTS__), output_index + 1):
                    self.__OUTPUTS__.update({i:deepcopy(MESSAGE())})

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
    
    def _receive_single(self, 
                        message: MESSAGE, 
                        index:int=-1) -> MESSAGE:
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
            if index>self._limits_inp:
                return message
            
        self.__REGISTER__.update({index : message})
        self.__ACTIVE_REGISTER__ = message
        
        return message

    def send(self, 
             message: Optional[Union[MESSAGE, List[MESSAGE]]] = None) -> Union[MESSAGE, List[MESSAGE]]:
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
                self.__OUTPUTS__ = {idx:msg for idx,msg in enumerate(message) if idx<self._limits_out}
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

            if index>=self._limits_inp:
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
            self.__OUTPUTS__ = {idx:_out for idx,_out in enumerate(out) if idx<self._limits_out}

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
    





