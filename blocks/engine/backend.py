import os
import sys
from abc import ABC, abstractmethod
from typing import Any, Callable, Dict, List, Optional, Union

from copy import deepcopy

import threading

import multiprocessing
from multiprocessing import Queue, Process, Pipe, Value, Array

from concurrent.futures import ThreadPoolExecutor

class Backend(ABC):
    """Base class for all execution backends."""
    
    __ntype__ = 'DEFAULTS'

    def __init__(self, **kwargs):
        """Initialize the backend with optional configuration."""
        self.config = kwargs

        self.running = False

    def to_dict(self) -> Dict[str, Any]:
        """Serialize the backend configuration to a dictionary."""
        return {
            'type': self.__class__.__name__,
            'config': deepcopy(self.config),
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Backend':
        """Deserialize the backend configuration from a dictionary."""
        config = data.get('config', {})
        return cls(**config)
        
    def setup(self, resources: Optional[Dict[str, Any]] = None) -> bool:
        """Set up the backend with necessary resources.
        
        Args:
            resources: Dictionary of resources needed by the backend
            
        Returns:
            bool: True if setup was successful, False otherwise
        """
        return True
    
    def _worker(self, *args, **kwargs) -> Any:
        """Internal worker method to be implemented by subclasses.
        
        Args:
            func: The function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result of the function execution
        """
        pass
        
    def execute(self, *args, **kwargs) -> Any:
        """Execute a function using this backend.
        
        Args:
            func: The function to execute
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            
        Returns:
            Any: Result of the function execution
        """
        result = self._worker( *args, **kwargs)
        #print(f"Execution result: {result}")
        return result
        
    def require(self, requirements: Dict[str, Any]) -> bool:
        """Check if the backend meets specific requirements.
        
        Args:
            requirements: Dictionary of requirements to check
            
        Returns:
            bool: True if all requirements are met, False otherwise
        """
        return True
        
    def destroy(self) -> None:
        """Clean up resources used by the backend."""
        pass





class JoblibBackend(Backend):

    __ntype__ = 'JOBLIB'

    def __init__(self, n_jobs=-1, backend_type='loky', **kwargs):
        super().__init__(**kwargs)
        self.n_jobs = n_jobs
        self.backend_type = backend_type

    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'type': self.__ntype__,
            'n_jobs': self.n_jobs,
            'backend_type': self.backend_type,
            'config': deepcopy(self.config),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Backend':
        return cls(
            n_jobs=data.get('n_jobs', -1),
            backend_type=data.get('backend_type', 'loky'),
            **data.get('config', {})
        )
    
    def execute(self, *args, **kwargs):
        
        pass

    
class ThreadedBackend(Backend):

    __ntype__ = 'THREADS'

    def __init__(self, 
                 max_workers=4, 
                 queue=None,
                 pool=None,
                 daemon=True,
                 **kwargs):
        print('Threads Backend is instanciated')
        
        super().__init__(**kwargs)
        
        self.max_workers = max_workers
        self.queue = queue if queue else Queue()
        self.pool = pool 
        self.daemon = daemon

    def to_dict(self):
        _dict = {}
        _dict.update({
            'type': self.__ntype__,
            'max_workers': self.max_workers,
            'daemon': self.daemon,
            'queue': None,
            'pool': type(self.pool).__name__ if self.pool else None,
        })
        return _dict
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Backend':
        return cls(
            max_workers=data.get('max_workers', 4),
            daemon=data.get('daemon', True),
            queue=data.get('queue', None),
            pool=data.get('pool', None),
            **data.get('config', {})
        )

    def setup(self, resources: Optional[Dict[str, Any]] = None) -> bool:
        if self.pool is None:
            self.pool = ThreadPoolExecutor(max_workers=self.max_workers,
                                           thread_name_prefix="ThreadedBackend")
            self.running = True
        return True

    def execute(self, func: Callable, *args, **kwargs) -> Any:

        self.setup()

        _worker = self._worker
        assert self.pool is not None
        future = self.pool.submit(_worker, func, *args, **kwargs)
        return future.result()
        
    def _worker(self, func, *args, **kwargs):
        
        try:
            result = func(*args, **kwargs)
            self.queue.put(('success', result, threading.current_thread().name))
            return result
        
        except Exception as e:
            self.queue.put(
                ('error', str(e), threading.current_thread().name))
            raise Exception

    def require(self, *args, **kwargs):
        return True

    def destroy(self,):
        
        if self.pool is not None:
            self.pool.shutdown()
            self.pool = None
        self.running = False


class MultiprocessBackend(Backend):
    __ntype__ = 'MULTIPROCESS'
    # Placeholder for multiprocess backend methods
    def __init__(self,):
        super().__init__()

    def to_dict(self) -> Dict[str, Any]:
        _dict = super().to_dict()
        return _dict

    def execute(self, func, *args, **kwargs):
        # Implementation for multiprocess execution
        pass

    def require(self, *args, **kwargs) -> bool:
        # Implementation for multiprocess requirements
        return True

    def destroy(self,):
        # Cleanup for multiprocess backend
        pass

class DistributedBackend(Backend):
    __ntype__ = 'DISTRIBUTED'
    # Placeholder for distributed backend methods
    def __init__(self,):
        super().__init__()

    def to_dict(self) -> Dict[str, Any]:
        _dict = super().to_dict()
        return _dict

    def execute(self, *args, **kwargs):
        # Implementation for distributed execution
        pass

    def require(self, *args, **kwargs) -> bool:
        # Implementation for distributed requirements
        return True

    def destroy(self,):
        # Cleanup for distributed backend
        pass

class GPUBackend(Backend):
    __ntype__ = 'CUDA'
    # Placeholder for GPU backend methods
    def __init__(self,):
        super().__init__()

    def to_dict(self) -> Dict[str, Any]:
        _dict = super().to_dict()
        return _dict

    def execute(self, *args, **kwargs):
        # Implementation for GPU execution
        pass

    def require(self, *args, **kwargs) -> bool:
        # Implementation for GPU requirements
        return True

    def destroy(self,):
        # Cleanup for GPU backend
        pass







