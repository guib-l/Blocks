import os
import sys
import typing
import abc
import copy
import json

from packages.package import Packages

from dataclasses import dataclass
from abc import ABC, abstractmethod

from tools.serializable import SerializableMixin, _std_serialize, _std_deserialize


class abstract_env(ABC,SerializableMixin):

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




class EnvPython(Packages,abstract_env):

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
    '''
    def __serialize__(self):
        """Méthode personnalisée pour sérialiser _python_env"""
        return {
            'directory': str(self.directory) if hasattr(self, 'directory') else '.',
            'env_name': self.env_name if hasattr(self, 'env_name') else 'pip-venv.01',
            'env_type': self.env_type if hasattr(self, 'env_type') else 'venv',
            'mng_type': self.mng_type if hasattr(self, 'mng_type') else 'pip',
            'dependencies': self.dependencies if hasattr(self, 'dependencies') else [],
            'auto_build': self.auto_build if hasattr(self, 'auto_build') else False,
            'profile': self.profile if hasattr(self, 'profile') else None
        }
    
    @classmethod
    def __deserialize__(cls, attributes):
        """Méthode personnalisée pour désérialiser _python_env"""
        from tools.serializable import _std_deserialize
        
        # Désérialiser les attributs
        deserialized = {
            k: _std_deserialize(v) for k, v in attributes.items()
        }
        
        # Créer une nouvelle instance
        return cls(**deserialized)

    '''






