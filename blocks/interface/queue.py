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

from blocks.interface.datapacket import DataPacket

from enum import Enum






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

    __ntype__ = "DATAQUEUE"

    def __init__(self):
        self._queue:List[Any] = []
        self._index:List[Any] = []
        self._lock = threading.Lock()

    def put(self, message:Any, label=None) -> None:
        """Ajoute un message à la file."""
        
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
    __ntype__ = "DATAPACKETQUEUE"

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


from queue import Queue

class QUEUE:
    QUEUE = Queue()
    DATAQUEUE = DataQueue()
    DATAPACKETQUEUE = DataPacketQueue()

    mapping = {
        'QUEUE': Queue(),
        'DATAQUEUE': DataQueue(),
        'DATAPACKETQUEUE': DataPacketQueue(),
    }
    
    @classmethod
    def get(cls, key):
        """Get queue by string key or return Queue if not found."""
        if not isinstance(key, str):
            return key
        
        return cls.mapping.get(key.upper(), Queue())
    


