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

_backend_available = {
    'default':Backend,
    'multiprocessing':MultiprocessBackend,
    'threads':ThreadedBackend,
    'distributed':DistributedBackend,
    'gpu':GPUBackend,
}

class AvailableBackend(Enum):
    default         = Backend,
    multiprocessing = MultiprocessBackend,
    threads         = ThreadedBackend,
    distributed     = DistributedBackend,
    gpu             = GPUBackend,



# TODO list:
# > Penser à faire une fonction submit pour soumettre les différentes taches
#   au processus du Backend
#   Cette méthode doit permettre d'éxécuter les nodes 
# > Implémenter la méthode d'éxécution qui permet gère la lecture/ecriture 
#   dans des fichier.
# ### > Proposer un backend d'éxécution sur un serveur via une gate SSH
# > Merge BaseExecute et Execute en une seule classe
 

class Execute(BaseExecute):

    def __init__(self,
                 queue = None,
                 backend='default',
                 build_backend=True,
                 *args, **kwargs):

        self._proto_backend  = self.select_backend(backend)

        if build_backend:
            self._backend = self.build_backend()

        if queue: 
            self._queue = queue
        else: 
            self._queue = Queue()

        super().__init__(*args,**kwargs)

        self._is_running = False

    def select_backend(self, name):

        if isinstance(name,str):
            try:
                return _backend_available[name]
            except:
                raise NotImplemented(f'Backend {name} is unknown')
        elif hasattr(name,'__object__'):
            return name
        else:
            raise NotImplemented

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
            raise NotImplementedError("No forward method provided for execution.")
        
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
    
    def to_dict(self):
        return dict(
            workdir=self.workdir,
            commands=copy.copy(self.commands),
            use_io=self.use_io,
            use_external=self.use_external,
            use_cache=self.use_cache,
        )


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
            raise NotImplementedError("No forward method provided for execution.")
        
        _exec = self._base_call(_mandat='execute')
        return _exec












