import os
import sys
import asyncio
import time
from typing import *
from abc import *

from enum import Enum


from blocks.base.prototype import Prototype


from blocks.utils.logger import *

from blocks.utils.exceptions import (InterfaceError,
                                     AdvanceInterfaceError,
                                     ErrorCodeInterface)



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

    __ntype__ = "SIMPLE"
    __slots__ = [
        '_node',
        'args',
        '_inputs',
        '_output',
        'ignore_keys',
        'ignore_conflict',
        'ignore_errors'
    ]

    def __init__(self, 
                 node:Prototype,
                 ignore_conflict:bool=False,
                 ignore_keys:List[str]=[],
                 ignore_errors:bool=True,
                 **arguments):
        
        logger.debug("Start to build Interface of node.")

        self._node: Prototype = node

        self.ignore_conflict = ignore_conflict
        self.ignore_keys = ignore_keys
        self.ignore_errors = ignore_errors

        self._inputs: Dict|None = {}
        self._output: Dict|None  = None

        self.args = arguments or {}
    
    @property
    def input(self)->Dict|None:
        return self._inputs if self._inputs else None
    
    @input.setter
    def input(self, message:Dict|None)->None:
        assert isinstance(message, (Dict,type(None))), \
            InterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_INPUT,
                message="Input must be a dict instance"
            )
        print(f"Updating input of node with message: {message}")
        self._inputs.update(message)

    @property
    def output(self)->Dict|None:
        return self._output if self._output else None
    
    @output.setter
    def output(self, message:Dict|None)->None:
        assert isinstance(message, (Dict,type(None))), \
            InterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_OUTPUT,
                message="Output must be a dict instance."
            )
        self._output = message


    # =========================================================================
    # Apply transformer on inputs

    def apply_transformer(self,
                          transformer:Optional[Callable]=None):
        if transformer and self._inputs:
            if callable(transformer):
                self._inputs = transformer(self._inputs)

    # =========================================================================
    # Execution and representation
    
    def execute(self,):
        if not self._inputs:
            raise InterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_EXECUTE,
                message="No input data provided."
            )
        
        try:
            print(f"Executing node '{self._node.name}' with input: {self._inputs}")
            results = self._node.execute(
                    **self.args, **self._inputs)
            
            if not isinstance(results, dict):
                logger.warning('Output concatenate into dict')
                results = {'result': results}
        
        except Exception as e:
            logger.critical("Execution error:", e)
            results = {'error': str(e)}

            if not self.ignore_errors:
                raise InterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_EXECUTE,
                    message="Error occurs in execution of Interface"
                )

        self.output = results

    async def async_execute(self,):
        if not self._inputs:
            raise ValueError("No input data provided.")
        
        try:
            results = await asyncio.to_thread(
                self._node.execute, **self.args, **self._inputs)
            if not isinstance(results, dict):
                logger.warning('Output concatenate into dict')
                results = {'result': results}
        
        except Exception as e:
            logger.critical("Asynchronous execution error:", e)
            results = {'error': str(e)}

            if not self.ignore_errors:
                raise InterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_EXECUTE,
                    message="Error occurs in execution of Interface"
                )

        self.output = results


    def __repr__(self):
        print_node = self._node.__repr__()
        txt = f"Interface[I/O](\n\tinput={self.input},\n\tnode={self._node.name},\n\toutput={self.output})"
        return txt








class INTERFACE:
    SIMPLE = Interface 
    mapping = {
            'SIMPLE': SIMPLE,
        }
    
    @classmethod
    def get(cls, key):
        """Get interface by string key or return Interface if not found."""
        if not isinstance(key, str):
            return Interface
        
        return cls.mapping.get(key.upper(), Interface)





