import os
import sys
import time
import asyncio
from copy import copy, deepcopy
from typing import Any, Dict, List, Optional

from blocks.utils.logger import *

from queue import Queue
from blocks.interface.buffer import BUFFER, DataBuffer, RedisDataBuffer


class CommunicationException(Exception):
    """Raise en error in Communication"""

class CommunicateGraphics(CommunicationException):
    """Raise en error in Graphics in Communication"""

class CommunicateInterface(CommunicationException):
    """Raise en error in Interface in Communication"""

class CommunicationEnter(CommunicationException):
    """Raise en error to start Communication"""

class CommunicationExit(CommunicationException):
    """Raise en error to exit Communication"""



class Communication:

    __ntype__ = 'COMMUNICATION'

    def __init__(self,
                 graphics=None,
                 interface=None,
                 buffer=None):
        
        self.graphics  = graphics
        self.buffer     = BUFFER.get(buffer)
        self.interface = interface 
        
    @property
    def interfaces(self):
        return self._interface

    @interfaces.setter
    def interfaces(self, interface):
        if interface is None:
            self._interface = []
        elif isinstance(interface,list):
            self._interface = interface
        elif isinstance(interface,dict):
            self.interface = [(k,v) for k,v in interface.items()]
        else:
            raise CommunicateInterface(
                "Interface must be a list or a dict with (index,interface) pairs.")
        
    def get_current_interface(self, label=None):
        if label is None:
            if self.graphics is not None:
                label = self.graphics.current_node.NAME
            else:
                raise CommunicateGraphics("Graphics must be defined to get current interface.")
        if self.interface is None:
            raise CommunicateInterface("No interface defined in LabelCommunication.")
        for lbl,intf in self.interface:
            if lbl == label:
                return intf
        raise CommunicateInterface(
            f"No interface found for label '{label}' in LabelCommunication.")

    def update_graphics(self, graphics):
        try:
            self.graphics = graphics
        except Exception as e:
            raise CommunicateGraphics("Failed to update graphics") from e

    def reset(self):
        self.buffer.reset()

    def __enter__(self):
        logger.debug("Successful open communications")
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.reset()
        logger.debug("Successful exit communications")
        



class DirectCommunication(Communication):

    __ntype__ = "DIRECT"

    def __init__(self,
                 graphics=None,
                 interface=None,
                 buffer=DataBuffer()):
        
        super().__init__(graphics=graphics,
                         interface=interface,
                         buffer=buffer)
        
    def send(self, data:Any, label=None):
        self.buffer.deposit(data, label=label)

    def receive(self,) -> Any:
        if self.buffer.has_data():
            return self.buffer.withdraw()
        return None

    def generator(self):

        if not self.graphics or not self.interface:
            raise CommunicateGraphics(
                "Graphics and interface must be defined for communication.")

        for _node in self.graphics:

            _label = _node.NAME \
                if hasattr(_node,'NAME') else str(_node)

            interf = self.get_current_interface(label=_label)
            
            interf.input = self.buffer.withdraw()

            print("      \033[1;30m\u2193\033[0m (followed by)",file=sys.stdout)

            yield interf


            try:
                _node.resolve(interf.output)
            except:
                pass

            if interf.output is not None:
                self.buffer.deposit(interf.output, label=_label)




class LabelCommunication(Communication):

    __ntype__ = "LABEL"

    def __init__(self,
                 graphics=None,
                 interface=None,
                 buffer=DataBuffer()):
        
        super().__init__(graphics=graphics,
                         interface=interface,
                         buffer=buffer)
        
    def send(self, data:Any, label=None):
        if label is None:
            if self.graphics is not None:
                label = self.graphics.first
        self.buffer.deposit(data, label=label)

    def receive(self, label=None, side='input') -> Any:
        if label is None:
            if self.graphics is not None:
                label = self.graphics.prev_node
        if self.buffer.has_data():
            return self.buffer.withdraw(label=label, side=side)
        return None
    
    def peek(self,label=None, side='input') -> Any:
        if label is None:
            raise ValueError(
                "Label must be provided for peeking data in LabelCommunication.")
        if self.buffer.has_data():
            return self.buffer.peek(label=label, side=side)
        else:
            raise CommunicationException(
                f"No data available in buffer for label '{label}'.")
        return None 
    
    def merge(self, 
              labels: List[Any],
              side: str = 'input',
              ignore_conflict=False,
              ignore_keys: List[str]=[]) -> Dict:
        
        merged_data = {}

        for label in labels:
            
            data = self.peek(label=label, side=side)

            if data is not None:
                for key, value in data.items():
                    if key not in merged_data and key not in ignore_keys:
                        merged_data[key] = value
                    else:
                        if not ignore_conflict:
                            raise KeyError(f"Key conflict during merge: {key}")
                        
                        if key not in ignore_keys:
                            merged_data[key] = value
        return merged_data


    def generator(self):

        if not self.graphics or not self.interface:
            raise CommunicateGraphics(
                "Graphics and interface must be defined for communication.")
        
        start = True

        for i,node in enumerate(self.graphics):
            
            if start:
                input = self.peek(label=node.NAME, side='input')
                start = False
            else:
                input = self.merge(labels=node.FROM, side='output')

            interf = self.get_current_interface(label=node.NAME)
            
            interf.input = input
            
            _prt_next='followed by'
            print(f"\t\033[1;30m\u2193\033[0m ({_prt_next})",file=sys.stdout)
            
            
            yield node,interf

            try:
                node.resolve(interf.output)
            except:
                pass

            if interf.output is not None:
                try:
                    self.buffer.deposit(
                        interf.output, 
                        label=self.graphics.current_node.NAME, 
                        side='output')
                except Exception as e:
                    print(f"Error putting output in buffer: {e}")




class AsyncCommunication(Communication):

    __ntype__ = "ASYNC"

    def __init__(self,
                 graphics=None,
                 interface=None,
                 buffer=None):
        super().__init__(graphics=graphics,
                         interface=interface,
                         buffer=buffer)
        
    def send(self, data:Any, label=None):
        if label is None:
            if self.graphics is not None:
                label = self.graphics.first
        self.buffer.deposit(data, label=label)

    def receive(self,label=None) -> Any:
        if label is None:
            if self.graphics is not None:
                label = self.graphics.prev_node
        if self.buffer.has_data():
            return self.buffer.withdraw(label=label)
        return None
    
    def peek(self,label=None, side='input') -> Any:
        if label is None:
            raise ValueError(
                "Label must be provided for peeking data in LabelCommunication.")
        if self.buffer.has_data():
            return self.buffer.peek(label=label, side=side)
        else:
            raise CommunicationException(
                f"No data available in buffer for label '{label}'.")
        return None 
    
    def merge(self, 
              labels: List[Any],
              side: str = 'input',
              ignore_conflict=False,
              ignore_keys: List[str]=[]) -> Dict:
        
        merged_data = {}

        for label in labels:
            
            data = self.peek(label=label, side=side)

            if data is not None:
                for key, value in data.items():
                    if key not in merged_data and key not in ignore_keys:
                        merged_data[key] = value
                    else:
                        if not ignore_conflict:
                            raise KeyError(f"Key conflict during merge: {key}")
                        
                        if key not in ignore_keys:
                            merged_data[key] = value
        return merged_data

    async def generator(self):

        if not self.graphics or not self.interface:
            raise ValueError(
                "Graphics and interface must be defined for communication.")

        for node_label in self.graphics:

            interf = None
            for label,intf in self.interface:
                if label == node_label:
                    interf = intf
                    break
            
            if interf is None:
                continue

            interf.input = await self.buffer.get()
            
            yield interf

            if interf.output is not None:
                await self.buffer.put(interf.output)



class SocketCommunication:
    ...




class COMMUNICATE:

    DIRECT=DirectCommunication
    LABEL=LabelCommunication
    ASYNC=AsyncCommunication
    SOCKET=SocketCommunication

    @classmethod
    def get(cls, key):
        """Get communication by string key or return Communication if not found."""
        if not isinstance(key, str):
            raise CommunicationException(
                "Key must be a string representing the communication type.")
        
        mapping = {
            'DIRECT': DirectCommunication,
            'LABEL': LabelCommunication,
            'ASYNC': AsyncCommunication,
            'SOCKET': SocketCommunication,
        }
        return mapping.get(key.upper(), DirectCommunication)





