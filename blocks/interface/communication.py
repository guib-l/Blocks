import os
import sys
import time
import asyncio
from copy import copy, deepcopy
from typing import *

from queue import Queue
from blocks.interface.queue import QUEUE,DataQueue,DataPacketQueue


class Communication:

    __ntype__ = 'COMMUNICATION'

    def __init__(self,
                 graphics=None,
                 interface=None,
                 queue=None):
        
        self.graphics  = graphics
        self.queue     = QUEUE.get(queue)
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
            raise TypeError(
                "Interface must be a list or a dict with (index,interface) pairs.")
        
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.queue.empty()



class DirectCommunication(Communication):

    __ntype__ = "DIRECT"

    def __init__(self,
                 graphics=None,
                 interface=None,
                 queue=Queue()):
        
        super().__init__(graphics=graphics,
                         interface=interface,
                         queue=queue)
        
    def send(self, data:Any, label=None):
        self.queue.put(data)

    def receive(self,) -> Any:
        if self.queue.not_empty:
            return self.queue.get()
        return None

    def generator(self):
        if not self.graphics or not self.interface:
            raise ValueError(
                "Graphics and interface must be defined for communication.")

        for node_label in self.graphics:

            for label,intf in self.interface:
                if label == node_label:
                    interf = intf
                    break
            
            interf.input = self.queue.get()
            
            yield interf

            if interf.output is not None:
                self.queue.put(interf.output)




class LabelCommunication(Communication):

    __ntype__ = "LABEL"

    def __init__(self,
                 graphics=None,
                 interface=None,
                 queue=DataQueue()):
        
        super().__init__(graphics=graphics,
                         interface=interface,
                         queue=queue)
        
    def send(self, data:Any, label=None):
        if label is None:
            label = self.graphics[0]
        self.queue.put(data, label=label)

    def receive(self,label=None) -> Any:
        if label is None:
            label = self.graphics[-1]
        if self.queue.not_empty:
            return self.queue.get(label=label)
        return None

    def generator(self):
        print('<<<<  graph : ',self.graphics)
        print('<<<< interf : ',self.interface)
        print()
        if not self.graphics or not self.interface:
            raise ValueError(
                "Graphics and interface must be defined for communication.")

        for i,node_label in enumerate(self.graphics):

            for label,intf in self.interface:
                if label == node_label:
                    interf = intf
                    break
            
            interf.input = self.queue.get(label=node_label)
            
            yield node_label,interf

            if interf.output is not None:
                try:
                    self.queue.put(interf.output, label=self.graphics[i+1])
                except IndexError:
                    self.queue.put(interf.output, label=self.graphics[i])



class AsyncCommunication(Communication):

    __ntype__ = "ASYNC"

    def __init__(self,
                 graphics=None,
                 interface=None,
                 queue=None):
        super().__init__(graphics=graphics,
                         interface=interface,
                         queue=queue)
        
    async def send(self, data:Any):
        pass

    async def receive(self,) -> Any:
        pass

    async def generator(self):

        if not self.graphics or not self.interface:
            raise ValueError(
                "Graphics and interface must be defined for communication.")

        for node_label in self.graphics:

            for label,intf in self.interface:
                if label == node_label:
                    interf = intf
                    break
            
            interf.input = await self.queue.get()
            
            yield interf

            if interf.output is not None:
                await self.queue.put(interf.output)



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
            return key
        
        mapping = {
            'DIRECT': DirectCommunication,
            'LABEL': LabelCommunication,
            'ASYNC': AsyncCommunication,
            'SOCKET': SocketCommunication,
        }
        return mapping.get(key.upper(), DirectCommunication)





