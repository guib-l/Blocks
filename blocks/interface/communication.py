import os
import sys
import time
import asyncio
from copy import copy, deepcopy
from typing import *

from blocks.interface.datapacket import DataQueue,DataPacketQueue






class DirectCommunication:

    def __init__(self,
                 graphics=None,
                 interface=None,
                 queue=DataQueue()):
        
        self.graphics  = graphics
        self.queue     = queue
        self.interface = interface if isinstance(interface,list) else [interface]

    def send(self, data:Any, label=None):
        self.queue.put(data)

    def receive(self,) -> Any:
        if self.queue.not_empty:
            return self.queue.get()
        return None

    def generator(self):

        if not self.graphics or not self.interface:
            raise ValueError("Graphics and interface must be defined for communication.")

        for node_label in self.graphics:

            for label,intf in self.interface:
                if label == node_label:
                    interf = intf
                    break
            
            interf.input = self.queue.get()
            
            yield interf

            if interf.output is not None:
                self.queue.put(interf.output)



    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        self.queue.empty()


    

class AsyncCommunication:

    async def send(self, data:Any):
        pass

    async def receive(self,) -> Any:
        pass




class SocketCommunication:
    ...




class COMMUNICATE:
    DIRECT=DirectCommunication
    ASYNC=AsyncCommunication
    SOCKET=SocketCommunication




