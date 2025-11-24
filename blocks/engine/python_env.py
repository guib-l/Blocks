import os
import sys
import typing
import abc
import copy
import json

from packages.package import Packages

from dataclasses import dataclass
from abc import ABC, abstractmethod


from serializable import simple_serializable

class abstract_env(ABC):

    @classmethod  
    @abstractmethod  
    def sub_build(cls, **kwargs):
        ...

    @abstractmethod
    def open(self,):
        ...

    @abstractmethod
    def close(self, **kwargs):
        ...
    
    @abstractmethod
    def create(self, **kwargs):
        ...

    @abstractmethod
    def update(self, **kwargs):
        ...



@dataclass
@simple_serializable
class _empty_env(abstract_env):

    @classmethod
    def sub_build(cls, **kwargs):
        return cls(**kwargs)
    
    def open(self,):
        print(f'> Open environment "Default"')

    def close(self, **kwargs):
        print(f'> Close environment "Default"')
    
    def create(self, **kwargs):
        print(f'> Create ')

    def update(self, **kwargs):
        print(f'> Update ')


class _python_env(Packages,abstract_env):

    def __init__(self, 
                 directory = '.',
                 env_name = 'pip-venv.01',
                 env_type = 'venv',
                 mng_type = 'pip',
                 dependencies = [],
                 auto_build = False,
                 profile = None,
                 **kwargs):
        
        super().__init__(directory=directory,
                         env_name=env_name,
                         env_type=env_type,
                         mng_type=mng_type,
                         dependencies=dependencies,
                         auto_build=auto_build,
                         profile=profile,
                         **kwargs)        

    @classmethod
    def sub_build(cls, **kwargs):
        _cls = cls(**kwargs)
        return _cls
    
    def open(self,):
        print(f'> Open environment  : "Python"')
        self.activate()

    def close(self,):
        print(f'> Close environment : "Python"')
        self.deactivate()
    
    def create(self, **kwargs):
        print(f'> Create Python environment ')
        self.build(**kwargs)

    def update(self, **kwargs):
        print(f'> Update Python environment ')

    # ============================================
    # Serialization of _python_env object








