
import threading
from datetime import *
from typing import *
from abc import *

import logging
import json

from blocks.utils.exceptions import optional_import

redis = optional_import("redis")





def get_new_label(exist_label:Any, new_label:Any=None) -> str:
    """Génère un label unique si aucun n'est fourni."""
    if exist_label is None:
        return 0
    
    if new_label is None:
        incr = 0
        label = len(exist_label)
        while label in exist_label:
            label = len(exist_label) + incr
            incr += 1
        return label
        
    return new_label


class Buffer(ABC):

    @abstractmethod
    def deposit(self, data: Any, label: Any = None, side: str = "input"):
        """Submit data to the buffer with an optional label and side."""
        ...

    @abstractmethod
    def withdraw(self, label: Any = None, side: str = "input"):
        """Withdraw data from the buffer based on the label and side."""
        ...

    @abstractmethod
    def peek(self, label: Any = None, side: str = "input"):
        """Peek at data in the buffer without removing it."""
        ...

    @abstractmethod
    def has_data(self, side: str = None):
        """Check if the buffer contains data."""
        ...


class DataBuffer(Buffer):

    def __init__(self):
        self._buffer = {
            "input":  {},   
            "output": {},    
        }
        self._lock = threading.Lock()

    def deposit(self, data: Any, label: Any = None, side: str = "input"):

        with self._lock:
            if label is None or label in self._buffer[side]:
                label = get_new_label(self._buffer[side], label)
            self._buffer[side][label] = data
            return label
        
    def withdraw(self, label: Any = None, side: str = "input"):

        with self._lock:
            slot = self._buffer[side]
            if not slot:
                return None
            if label is not None:
                return slot.pop(label, None)
            first = next(iter(slot))
            return slot.pop(first)

    def peek(self, label: Any = None, side: str = "input"):

        with self._lock:
            slot = self._buffer[side]
            if not slot:
                return None
            if label is not None:
                return slot.get(label, None)
            return next(iter(slot.values()))

    def has_data(self, side: str = None):
        
        with self._lock:
            if side:
                return len(self._buffer[side]) > 0
            return any(len(v) > 0 for v in self._buffer.values())

    def flush(self, side: str = None):
        
        with self._lock:
            if side:
                self._buffer[side].clear()
            else:
                self._buffer = {"input": {}, "output": {}}

    def labels(self, side: str = "input") -> List[Any]:

        with self._lock:
            return list(self._buffer[side].keys())
    
    def is_empty(self, side: str = None) -> bool:
        
        with self._lock:
            if side:
                return len(self._buffer[side]) == 0
            return all(len(v) == 0 for v in self._buffer.values())
    
    def reset(self):
        
        with self._lock:
            self._buffer = {"input": {}, "output": {}}

    def __repr__(self):
        return (
            f"DataBuffer("
            f"input={len(self._buffer['input'])}, "
            f"output={len(self._buffer['output'])})"
        )



class RedisDataBuffer(Buffer):

    def __init__(
        self,
        namespace: str = "databuffer",
        host: str = "localhost",
        port: int = 6379,
        db: int = 0,
        password: str = None,
        ttl: int = None,    
    ):
        
        if redis is None:
            raise ImportError(
                "Redis library not found. Please install it with 'pip install redis' "
                "to use RedisDataBuffer."
            )
        
        self._namespace = namespace
        self._ttl = ttl
        self._client = redis.Redis(
            host=host,
            port=port,
            db=db,
            password=password,
            decode_responses=True   # retourne des str et non des bytes
        )
        self._lock = threading.Lock()

    def _key(self, side: str) -> str:
        
        return f"{self._namespace}:{side}"

    def _new_label(self, side: str) -> str:
        
        counter_key = f"{self._namespace}:{side}:counter"
        return str(self._client.incr(counter_key))

    def deposit(self, data: Any, label: Any = None, side: str = "input"):

        with self._lock:
            key = self._key(side)

            if label is None or self._client.hexists(key, str(label)):
                label = self._new_label(side)

            self._client.hset(key, str(label), json.dumps(data))

            if self._ttl:
                self._client.expire(key, self._ttl)

            return label

    def withdraw(self, label: Any = None, side: str = "input") :
        with self._lock:
            key = self._key(side)

            if label is not None:
                raw = self._client.hget(key, str(label))
                if raw is None:
                    return None
                self._client.hdel(key, str(label))
                return json.loads(raw)

            labels = self._client.hkeys(key)
            if not labels:
                return None
            first = labels[0]
            raw = self._client.hget(key, first)
            self._client.hdel(key, first)
            return json.loads(raw)

    def peek(self, label: Any = None, side: str = "input"):
        
        with self._lock:
            key = self._key(side)

            if label is not None:
                raw = self._client.hget(key, str(label))
                return json.loads(raw) if raw else None

            labels = self._client.hkeys(key)
            if not labels:
                return None
            raw = self._client.hget(key, labels[0])
            return json.loads(raw) if raw else None

    def has_data(self, side: str = None):
    
        with self._lock:
            if side:
                return self._client.hlen(self._key(side)) > 0
            return any(
                self._client.hlen(self._key(s)) > 0
                for s in ("input", "output")
            )

    def flush(self, side: str = None):
        with self._lock:
            if side:
                self._client.delete(self._key(side))
            else:
                self._client.delete(self._key("input"))
                self._client.delete(self._key("output"))

    def labels(self, side: str = "input") :
        with self._lock:
            return self._client.hkeys(self._key(side))

    def ping(self):
        try:
            return self._client.ping()
        except redis.ConnectionError:
            return False

    def __repr__(self):
        input_len  = self._client.hlen(self._key("input"))
        output_len = self._client.hlen(self._key("output"))
        return (
            f"RedisDataBuffer(namespace='{self._namespace}', "
            f"input={input_len}, output={output_len})"
        )

    def reset(self):
        self.flush()




from queue import Queue

class QUEUE:
    mapping = {
        'DATABUFFER': DataBuffer(),
        'REDISBUFFER': RedisDataBuffer,
    }
    
    @classmethod
    def get(cls, key):
        """Get queue by string key or return Queue if not found."""
        if not isinstance(key, str):
            return key
        
        return cls.mapping.get(key.upper(), Queue())
    


