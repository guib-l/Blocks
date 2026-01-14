import os
import sys
import typing
import abc
import copy
import time

import subprocess
from typing import final,overload
from dataclasses import dataclass
from abc import abstractmethod

from pathlib import Path

from . import (ExecutionError,
               ExecutionSetupError,
               ExecutionFailed,
               InputError,
               OutputError,
               ExecutionNotFound,)

import multiprocessing
from multiprocessing import Queue, Process, Pipe, Value, Array

from enum import Enum


class BaseExecute:

    __ntype__ = 'BaseExecute'
    
    def __init__(self, 
                 workdir=None,
                 commands=None,
                 use_io=True,
                 use_external=False,
                 use_cache=False,
                  **kwargs):
                
        self.workdir = workdir or ""

        if not os.path.exists(self.workdir) and use_io:
            raise ExecutionSetupError(
                f"Work directory '{self.workdir}' didn't exists.")

        self.commands      = commands
        self.use_external  = use_external
        self.use_io        = use_io
        self.use_cache     = use_cache


    # -------------------------------------------------------------------------
    # Serializable / Copy functions

    def to_config(self):
        return {}
    
    def to_dict(self,):
        results = {}
        return results

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)

    def copy(self,):
        return type(self)(
            workdir=self.workdir,
            commands=copy.copy(self.commands),
            use_io=self.use_io,
            use_external=self.use_external,
            use_cache=self.use_cache,
        )

    # -------------------------------------------------------------------------
    # Properties of Executor

    @property
    def workdir(self) -> str:
        return self._workdir

    @workdir.setter
    def workdir(self, workdir):
        self._workdir = str(Path(workdir))  

    def __str__(self):
        txt = f"Execute(workdir={self.workdir}, use_external={self.use_external}, language={self.language})"
        return txt


from .backend import Backend
from .backend import (ThreadedBackend, 
                      MultiprocessBackend, 
                      DistributedBackend, 
                      GPUBackend)

class EXECUTE_BACKEND:
    DEFAULT         = Backend,
    MULTIPROCESSING = MultiprocessBackend,
    THREADS         = ThreadedBackend,
    DISTRIBUTED     = DistributedBackend,
    GPU             = GPUBackend,

    mapping = {
        'DEFAULT':Backend,
        'MULTIPROCESSING':MultiprocessBackend,
        'THREADS':ThreadedBackend,
        'DISTRIBUTED':DistributedBackend,
        'GPU':GPUBackend,
    }
    
    @classmethod
    def get(cls, key):
        """Get communication by string key or return Communication if not found."""
        if not isinstance(key, str):
            return key
        
        return cls.mapping.get(key.upper(), Backend)



# TODO list:
# > Penser à faire une fonction submit pour soumettre les différentes taches
#   au processus du Backend
#   Cette méthode doit permettre d'éxécuter les nodes 
# > Implémenter la méthode d'éxécution qui permet gère la lecture/ecriture 
#   dans des fichier.
# ### > Proposer un backend d'éxécution sur un serveur via une gate SSH
# > Merge BaseExecute et Execute en une seule classe
 


class Execute(BaseExecute):

    __ntype__ = 'Execute'

    def __init__(self,
                 queue = None,
                 backend='DEFAULT',
                 build_backend=True,
                 **kwargs):

        self._proto_backend  = EXECUTE_BACKEND.get(backend)

        if build_backend:
            self._backend = self.build_backend()

        if queue: 
            self._queue = queue
        else: 
            self._queue = Queue()

        super().__init__(**kwargs)

        self._is_running = False

    def to_config(self):
        return {}

    def to_dict(self):
        return dict(
            workdir=self.workdir,
            commands=copy.copy(self.commands),
            use_io=self.use_io,
            use_external=self.use_external,
            use_cache=self.use_cache,
            backend=self._backend.to_dict() or None,
            queue=(lambda: self._queue.to_dict())() if not Exception else None,
            build_backend=True,
        )
    
    @classmethod
    def from_dict(cls, **data):
        backend_data = data.get('backend', {})
        backend = EXECUTE_BACKEND.get(backend_data.get('type', 'DEFAULT'))
        return cls(
            workdir=data.get('workdir', None),
            commands=data.get('commands', None),
            use_io=data.get('use_io', True),
            use_external=data.get('use_external', False),
            use_cache=data.get('use_cache', False),
            backend=backend,
            build_backend=True,
        )


    def _base_call(self, _mandat=''):
        try:
            return getattr(self._backend, _mandat)
        except:
            raise NotImplemented
        return None

    # -------------------------------------------------------------------------
    # Basic methods of Executor

    def execute(self, forward=None):
        
        if forward:
            self._backend._worker = forward
        else:
            raise NotImplementedError(
                "No forward method provided for execution.")
        
        _exec = self._base_call(_mandat='execute')
        return _exec

    def build_backend(self, *args, **kwargs):

        self._backend = self._proto_backend(*args, **kwargs)
        return self._backend
    
        #_setup = self._base_call(_mandat='setup')
        #_setup()

    def __str__(self):
        txt = f"Execute(backend={self._proto_backend};"
        return txt
    

class FileIOExecute(Execute):

    def write_input(self,):
        pass

    def read_output(self,):
        pass
    
    @overload
    def execute(self, forward=None):
        
        if forward:
            self._backend._worker = forward
        else:
            raise NotImplementedError(
                "No forward method provided for execution.")
        
        _exec = self._base_call(_mandat='execute')
        return _exec












