import os
import sys
import typing

import subprocess
from abc import abstractmethod

from pathlib import Path

from . import (ExecutionError,
               ExecutionSetupError,
               ExecutionFailed,
               InputError,
               OutputError,
               ExecutionNotFound,)


from blocks.base.signal import Signal



class BaseExecute(object):
    
    def __init__(self, 
                 workdir=None, 
                 commands=None, 
                 use_shell=False, 
                 langage=None,
                 signal=None,
                  **kwargs):
                
        self.workdir = workdir or ""

        if not os.path.exists(self.workdir):
            raise ExecutionSetupError(
                f"Work directory '{self.workdir}' didn't exists.")
        
        self.commands   = commands
        self.use_shell  = use_shell
        self.langage    = langage 
        self.parameters = kwargs.copy()

        # Initialisation du signal
        self.sgl = signal

        if signal is None:
            self.sgl = Signal('LOADED')

    def to_dict(self,):
        results = {
            'workdir':self.workdir,
            'use_shell':self.use_shell,
            'langage':self.langage,
            'commands':self.commands, }
        results.update(**self.parameters)
        return results

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)

    def copy(self,):
        ...

    def deepcopy(self,):
        ...


    # -----------------------------------------------------
    # signal methods
    # Méthodes pour accéder et modifier l'état du node 
    # via le signal

    @property
    def signal(self):
        self.__SIGNAL__ = self.sgl.signal
        return self.__SIGNAL__

    @signal.setter
    def signal(self, value):
        self.sgl.signal = value
        self.__SIGNAL__  = value
        
    @property
    def langage(self) -> str:
        """
        Get the langage of the execution.
        """
        return self._langage
    
    @langage.setter
    def langage(self, langage: str):
        """
        Set the langage of the execution.
        """
        #if langage not in _supported_languages:
        #    raise ExecutionError(f"Invalid langage '{langage}'.")
        self._langage = langage

    @property
    def workdir(self) -> str:
        return self._workdir

    @workdir.setter
    def workdir(self, workdir):
        self._workdir = str(Path(workdir))  



    @abstractmethod
    def require(self,):
        self.signal = "required".upper()
        ...

    @abstractmethod
    def destroy(self,):
        self.signal = "destroyed".upper()
        ...

    @abstractmethod
    def load(self,):
        self.signal = "loaded".upper()
        ...

    @abstractmethod
    def interrupt(self,):
        self.signal = "interrupted".upper()
        ...

    @abstractmethod
    def execute(self,):
        self.signal = "running".upper()
        ...




class FileIOExecute(BaseExecute):
    ...


class Execute(BaseExecute):
    ...






