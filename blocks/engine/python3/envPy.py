import os
import sys
import typing
import abc
import copy
import json

from packages.package import Packages

from dataclasses import dataclass
from abc import ABC, abstractmethod

from blocks.utils.logger import *



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
class EnvEmpty(abstract_env):

    __ntype__ = "empty_env"

    @classmethod
    def sub_build(cls, **kwargs):
        return cls(**kwargs)
    
    def open(self,):
        env_logger.info(f'Open empty environment')
        ...

    def close(self, **kwargs):
        env_logger.info(f'Close empty environment')
        ...
    
    def create(self, **kwargs):
        env_logger.info(f'Create empty environment')
        ...

    def update(self, **kwargs):
        env_logger.info(f'Update empty environment')
        ...




class EnvPython(Packages,abstract_env):

    __ntype__ = "python_env"

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
        self.activate()

    def close(self,):
        self.deactivate()
    
    def create(self, **kwargs):
        self.build(**kwargs)

    def update(self, **kwargs):
        env_logger.warning(f'This do nothing')
        pass

    def to_dict(self,):
        return self.package_to_dict()







