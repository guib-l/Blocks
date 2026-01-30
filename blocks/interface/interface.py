import os
import sys
import asyncio
import time
from typing import *
from abc import *

from enum import Enum


from blocks.interface.datapacket import (DataPacket,
                                         DataPacketPriority,
                                         DataPacketType)
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

        self.args = arguments or None
    
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







class AdvancedInterface(Interface):

    __ntype__ = "ADVANCED"
    __slots__ = [
        '_node',
        '_inputs',
        '_output',
        '_error',
        '_production',
        'actual_destination',
        'ignore_keys',
        'ignore_conflict',
        'ignore_errors',
    ]
    
    def __init__(self, 
                 node:Prototype,
                 ignore_conflict:bool=False,
                 ignore_errors:bool=True,                 
                 ignore_keys:List[str]=[]):
        
        super().__init__(node=node,
                         ignore_conflict=ignore_conflict,
                         ignore_keys=ignore_keys,
                         ignore_errors=ignore_errors)
        
        self._inputs: List[DataPacket] = []
        self._output: DataPacket|None  = None
        self._error: DataPacket|None   = None
    
    
    @property
    def input(self)->DataPacket|None:
        return self._inputs if self._inputs else None
    
    @input.setter
    def input(self, message:DataPacket|None)->None:
        assert isinstance(message, (DataPacket,type(None))), \
            AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_INPUT,
                message="Input must be a DataPacket instance."
            )
            
        self._inputs.append(message)

    @property
    def output(self)->DataPacket|None:
        return self._output if self._output else None
    
    @output.setter
    def output(self, message:DataPacket|None)->None:
        assert isinstance(message, (DataPacket,type(None))), \
            AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_OUTPUT,
                message="Output must be a DataPacket instance."
            )
        self._output = message

    @property
    def error(self)->DataPacket|None:
        return self._error
    
    @error.setter
    def error(self, message:DataPacket|None)->None:
        assert isinstance(message, (DataPacket,type(None))), \
            AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR,
                message="Error must be a DataPacket instance."
            )
            
        self._error = message


    # =========================================================================
    # Input merging

    def merge_inputs(self,):

        msg = self._inputs[0].DATA if self._inputs else {}

        for message in self._inputs[1:]:
            msg = message.merge_data(msg,
                                     ignore_conflict=self.ignore_conflict, 
                                     ignore_keys=self.ignore_keys)

        return msg

    # =========================================================================
    # Handlers for transformations, delays, expirations

    def handler_transform(self,
                          message:DataPacket|None= None,
                          transformer=None):
        
        if transformer and message:
            if callable(transformer):
                try:
                    message.DATA = transformer(message.DATA)
                except Exception as e:
                    logger.critical("Cannot transform message properly.")
                    raise AdvanceInterfaceError(
                        code=ErrorCodeInterface.INTERFACE_ERROR_TRANSFORMER,
                        message="Cannot transform message properly.",
                        cause=e,
                    ) 

            elif isinstance(transformer, list):
                for func in transformer:
                    try:
                        message.DATA = func(message.DATA)
                    except Exception as e:
                        logger.critical("Cannot transform message properly.")
                        raise AdvanceInterfaceError(
                            code=ErrorCodeInterface.INTERFACE_ERROR_TRANSFORMER,
                            message="Cannot transform message properly.",
                            cause=e,
                        )
            else:
                logger.critical("Transformer is not a Callable or List[Callable]")
                raise AdvanceInterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_TRANSFORMER,
                    message="Transformer is not a Callable or List[Callable]",
                )
        return message
    
    def handler_delay(self,
                      message:DataPacket|None= None,
                      delay=None):
        time.sleep(delay if delay else 0)
        return message

    def handler_expire(self,
                       message:DataPacket|None= None,
                       expire_time=None):
        
        if expire_time and message:
            current_time = time.time()

            if current_time + message.DELAY > expire_time:
                logger.critical("Message has expired")
                raise AdvanceInterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_TIMEOUT,
                    message="Message has expired."
                )
        return message

    # =========================================================================
    # Apply handlers on all inputs

    def apply_expire(self,
                     expire_time=0):
        for idx, message in enumerate(self._inputs):
            try:
                message = self.handler_expire(message=message, 
                                expire_time=getattr(message,'EXPIRY', expire_time))
                self._inputs[idx] = message
            except TimeoutError as e:
                logger.critical(f"Message expired and removed: {message}")
                raise AdvanceInterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_TIMEOUT,
                    message="Message has expired and removed.",
                    cause=e
                )

    def apply_transform(self,
                        transformer=None):
        
        for idx, message in enumerate(self._inputs):
            try:
                message = self.handler_transform(message=message, 
                                transformer=getattr(message,'TRANSFORM') or transformer)
                self._inputs[idx] = message
            except:
                logger.critical("Transformation failed on message:", message)
                raise AdvanceInterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_TRANSFORMER,
                    message=f"Transformation failed on message: {message}",
                )

    def apply_delay(self,
                    delay=0.0):
        
        delay_list = [getattr(msg, 'DELAY') or delay for msg in self._inputs]
        max_delay = max(delay_list) if delay_list else 0

        min_expire = min([getattr(msg, 'EXPIRY') or float('inf') 
                      for msg in self._inputs])
        
        if max_delay >= min_expire:
            logger.warning("Applied delay may cause message expiration.")

        try:
            self.handler_delay(message=None, 
                            delay=max_delay)
        except:
            logger.critical(f"Delay application failed on message: {max_delay}")
            raise AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_TIMEOUT,
                message=f"Delay application failed on message: {max_delay}",
            )


    def check_destination(self,):
        _desitination = []
        for message in self._inputs:
            _desitination.append(message.TO)
        
        if len(set(_desitination)) > 1 and not self.ignore_conflict:
            raise AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR_TIMEOUT,
                message=f"Conflicting destinations in input messages.",
            )

        self.actual_destination = _desitination[0] if _desitination else None

    # =========================================================================
    # Execution and representation

    def execute(self, delay=0, transformer=None, expire_time=0):
        """Execution of the node with input processing."""
        start_time = time.time()
        
        self.check_destination()

        logger.info("Apply handlers of Interfaced node")

        # Apply delay
        self.apply_delay(delay=delay)
        
        # Apply transformations and expiration checks
        self.apply_transform(transformer=transformer)
        self.apply_expire(expire_time=expire_time)

        # Merge inputs and execute
        _data = self.merge_inputs()

        end_time = time.time()
        actual_delay = end_time - start_time
        logger.debug(f"Actual delay applied: {actual_delay} seconds.")

        try:
            results = self._node.execute(**_data)
            if not isinstance(results, dict):
                results = {'result': results}
        except Exception as e:
            logger.critical(f"Execution error: {e}")
            results = {'error': str(e)}

            if not self.ignore_errors:
                raise AdvanceInterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_EXECUTE,
                    message="Error occurs in execution of AdvancedInterface"
                )


        self._production = results
        return results



    # Execution asynchrones
    async def async_execute(self, delay=0, transformer=None, expire_time=0):
        """Asynchronous execution of the node with input processing."""
        
        self.check_destination()
        
        logger.info("Apply handlers of AdvancedInterfaced node")

        # Apply delay asynchronously
        if delay > 0:
            await asyncio.sleep(delay)
        
        # Apply transformations and expiration checks
        self.apply_transform(transformer=transformer)
        self.apply_expire(expire_time=expire_time)
        
        # Merge inputs and execute
        _data = self.merge_inputs()
        
        try:
            # Execute node (wrap sync execution if needed)
            results = await asyncio.to_thread(self._node.execute, **_data)
            if not isinstance(results, dict):
                results = {'result': results}
        except Exception as e:
            logger.critical(f"Asynchronous execution error: {e}")
            results = {'error': str(e)}

            if not self.ignore_errors:
                raise AdvanceInterfaceError(
                    code=ErrorCodeInterface.INTERFACE_ERROR_EXECUTE,
                    message="Error occurs in execution of AdvancedInterface"
                )

        self._production = results
        return results
        



    def product_output(self, 
                       TO=None,
                       SUBJECT=None,
                       TYPE=DataPacketType.DIRECT,
                       TRANSFORM:Optional[Callable]=None,
                       ASYNC:bool=False) -> DataPacket:
        
        if not self._production:
            raise AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR,
                message="No production data available. Execute the node first."
            )
        if TO is None:
            raise AdvanceInterfaceError(
                code=ErrorCodeInterface.INTERFACE_ERROR,
                message="Output 'TO' field must be specified."
            )
        
        if 'error' in self._production:
            self.error = DataPacket.generate_error(
                FROM=self._node.id,
                error=self._production['error'],
                DATA={k:v for k,v in self._production.items() if k!='error'},
                PRIORITY=DataPacketPriority.HIGH,
            )
            return self._error
        
        self.output =  DataPacket.generate_message(
            FROM=self.actual_destination or self._node.id,
            TO=TO,
            DATA=self._production,
            SUBJECT=SUBJECT or f"Output from {self._node.name}",
            TYPE=TYPE,
            TRANSFORM=TRANSFORM,
            ASYNC=ASYNC,
            PRIORITY=DataPacketPriority.NORMAL
        )
        return self._output



class INTERFACE:
    SIMPLE = Interface 
    ADVANCED = AdvancedInterface
    mapping = {
            'SIMPLE': SIMPLE,
            'ADVANCED': ADVANCED,
        }
    
    @classmethod
    def get(cls, key):
        """Get interface by string key or return Interface if not found."""
        if not isinstance(key, str):
            return Interface
        
        return cls.mapping.get(key.upper(), Interface)





