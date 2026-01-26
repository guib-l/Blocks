import os
import sys
import copy

from typing import overload
from pathlib import Path

from multiprocessing import Queue

from blocks.utils.logger import *

from blocks.utils.exceptions import safe_operation
from blocks.utils.exceptions import (ErrorCodeExec,
                                     ExecutionError)


from .backend import Backend
from .backend import (ThreadedBackend, 
                      MultiprocessBackend, 
                      DistributedBackend, 
                      GPUBackend)

from blocks.utils.logger import *


# TODO:
# > Penser à faire une fonction submit pour soumettre les différentes taches
#   au processus du Backend
#   Cette méthode doit permettre d'éxécuter les nodes 
# > Implémenter la méthode d'éxécution qui permet gère la lecture/ecriture 
#   dans des fichier.


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
        """
        Get communication by string key or return Communication 
        if not found.
        """
        if not isinstance(key, str):
            return key
        
        return cls.mapping.get(key.upper(), Backend)




class BaseExecute:

    __ntype__ = 'BaseExecute'
    
    def __init__(self, 
                 *,
                 workdir=None,
                 commands=None,
                 use_io=True,
                 use_external=False,
                 use_cache=False,
                  **kwargs):
                
        self.workdir = workdir or ""

        if not os.path.exists(self.workdir) and use_io:
            raise ExecutionError(
                code=ErrorCodeExec.EXECUTE_ERROR_INIT,
                message=f"Work directory '{self.workdir}' didn't exists.")

        self.commands      = commands
        self.use_external  = use_external
        self.use_io        = use_io
        self.use_cache     = use_cache


    # -------------------------------------------------------------------------
    # Serializable / Copy functions

    def to_config(self):
        return {
            'workdir':self.workdir,
            'commands':copy.copy(self.commands),
            'use_io':self.use_io,
            'use_external':self.use_external,
            'use_cache':self.use_cache,
        }
    
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



 

class Execute(BaseExecute):

    __ntype__ = 'Execute'

    def __init__(self,
                 queue = Queue(),
                 backend='DEFAULT',
                 build_backend=True,
                 ignore_warning=True,
                 **kwargs):

        exec_logger.info("Loading Executor method")

        if isinstance(backend,str):
            self._proto_backend  = EXECUTE_BACKEND.get(backend)
            arguments = {}

        elif isinstance(backend,dict):
            self._proto_backend = EXECUTE_BACKEND.get(
                backend.pop('type', 'DEFAULT'))
            arguments = backend
        else:
            
            exec_logger.warning("Loading Executor Error : unknow Backend")
            exec_logger.warning("Automatic selection of defaults")
            
            if not ignore_warning:
                raise ExecutionError(
                    code=ErrorCodeExec.EXECUTE_ERROR_INIT,
                    message=f"Unknow Executor object")


        if build_backend:
            self._backend = self.build_backend(**arguments)

        self._queue = queue

        super().__init__(**kwargs)


    def to_config(self):
        config = super().to_config()
        return config.update(**self.to_dict())

    def to_dict(self):

        with safe_operation(
                'Compose dict of executor',
                code=ErrorCodeExec.EXECUTE_ERROR_SERIALIZATION,
                ERROR=ExecutionError ):

            _dict = dict(
                workdir=self.workdir,
                commands=copy.copy(self.commands),
                use_io=self.use_io,
                use_external=self.use_external,
                use_cache=self.use_cache,
                backend=self._backend.to_dict() or None,
                queue=(lambda: self._queue.to_dict())() if not Exception else None,
                build_backend=True,
            )
            return _dict
    
    @classmethod
    def from_dict(cls, **data):

        with safe_operation(
                'loading executor',
                code=ErrorCodeExec.EXECUTE_ERROR_DESERIALIZATION,
                ERROR=ExecutionError ):

            return cls(
                workdir=data.pop('workdir', None),
                commands=data.pop('commands', None),
                use_io=data.pop('use_io', True),
                use_external=data.pop('use_external', False),
                use_cache=data.pop('use_cache', False),
                backend=data.pop('backend',{}),
                **data
            )


    def _base_call(self, _mandat=''):
        try:
            return getattr(self._backend, _mandat)
        except:
            exec_logger.critical(f"Unknow attribute {_mandat}")
            raise ExecutionError(
                code=ErrorCodeExec.EXECUTE_ERROR_IMPLEMENT,
                message=f"Attribute {_mandat} unfounded.")
        return None

    # -------------------------------------------------------------------------
    # Basic methods of Executor

    def execute(self, forward=None):
                
        if forward:
            exec_logger.info("Feed worker with forward method")
            self._backend._worker = forward
        else:
            exec_logger.critical("Forward method is mandatory")
            raise ExecutionError(
                code=ErrorCodeExec.EXECUTE_ERROR_IMPLEMENT,
                message="No forward method provided for execution.")
        
        return self._base_call(_mandat='execute')

    def build_backend(self, **kwargs):

        try:
            exec_logger.info("Build Backend object")
            self._backend = self._proto_backend(**kwargs)
        except:
            exec_logger.critical("Forward method is mandatory")
            raise ExecutionError(
                code=ErrorCodeExec.EXECUTE_ERROR_BUILD,
                message="Backend cannot be build: turn off relative attribute")
            
        return self._backend
    
    def __str__(self):
        txt = f"Execute(backend={self._proto_backend.__ntype__});"
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












