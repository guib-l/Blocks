import os
import sys
import typing
import abc
import copy
import json

import inspect
import importlib.util
from pathlib import Path

from enum import Enum,Flag

from blocks.engine import PYTHON

from tools.serializable import SerializableMixin

from tools.encoder import EnvJSONEncoder




class Environ:

    __environ__ = PYTHON

    def __init_env__(self,
                     backend_env=PYTHON,
                     **kwargs):
        
        self.env = backend_env
        _backend = backend_env.environment

        self.env.parameters.update(**kwargs)

        self.backend = _backend( **self.env.parameters ) 


    # ============================================
    # Variables definition

    @property
    def env(self,):
        return self.__environ__

    @env.setter
    def env(self, new_env):
        self.__environ__ = new_env

    # Define alias
    environment = env


    # ============================================
    # Definition Build-in functions

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):        
        try:
            self.close()
        except:
            raise EnvironmentError("Not closed env.")

    def __call__(self, _mandat=''):
        try:
            return getattr(self.backend, _mandat)
        except:
            raise NotImplementedError(
                f'Method {_mandat} not in object {self.backend.__class__}')
   
    def __diff__(self, other):
        # Check si tout les paramètres sont identiques
        if other == self.env:
            return True
        else:
            if other.language == self.env.language:
                if other.environment == self.env.environment:
                    return True
            
        return False

    def __mix__(self, other):
        # Ajoute les fonctions de 'other' dans self
        # a condition que tout les paramètres soient identiques

        return self


    # ============================================
    # Copy of Environment object

    def copy(self,):
        _env = type(self)(
            backend_env=self._backend_env,)
        return _env
   
    # ============================================
    # Standard function from Backend attribute

    def open(self):
        value =  self.__call__("open")
        return value()

    def close(self,):
        value = self.__call__("close")
        return value()
    
    def create(self, **kwargs):
        value = self.__call__("create")
        return value(**kwargs)
    
    def update(self,**kwargs):
        value = self.__call__("update")
        return value(**kwargs)


class Environment(Environ,SerializableMixin):

    __slots__ = (
        'name',
        'language',
        'backend_env',
    )

    def __init__(self,
                 name='env',
                 language='python3', 
                 backend_env=PYTHON,
                 **kwargs):
         
         super().__init_env__(
             backend_env=backend_env,
             **kwargs
         )
         self.name = name
         self.language = language

















