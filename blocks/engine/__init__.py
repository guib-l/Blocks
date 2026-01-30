import os
import sys
import json

from enum import Enum

from .envPy import EnvEmpty,EnvPython
from tools.serializable import SerializableMixin




class Language:
    PYTHON   = 'python'
    R        = 'r'
    JULIA    = 'julia'
    MATLAB   = 'matlab'
    BASH     = 'bash'

    @classmethod
    def get(cls, key):
        if not isinstance(key, str):
            return key
        
        mapping = {
            'PYTHON': cls.PYTHON,
            'R': cls.R,
            'JULIA': cls.JULIA,
            'MATLAB': cls.MATLAB,
            'BASH': cls.BASH,
        }
        return mapping.get(key.upper(), PYTHON)




class PYTHON:
    """
    Python environment configuration
        - environment : EnvPython
        - language    : Language.PYTHON
        - parameters  : dict(empty)
    """
    environment = EnvEmpty
    language    = Language.PYTHON
    parameters  = {}

class PYTHON_PIP:
    """
    Python environment configuration with pip package manager
        - environment : EnvPython
        - language    : Language.PYTHON
        - parameters  : dict with pip settings
    """
    environment = EnvPython
    language    = Language.PYTHON
    parameters  = {
        'directory': '.',
        'env_name': 'generic-env.01',
        'env': 'venv',
        'mng': 'pip',
        'dependencies': [],
        'auto_build': True,
        'profile': None,
    }


class ENVIRONMENT_TYPE:
    """
    Environment types available in Blocks Engine.
        - PYTHON : Basic Python environment
        - PYTHON_PIP : Python environment with pip package manager
    """
    
    PYTHON = PYTHON
    PYTHON_PIP = PYTHON_PIP

    @classmethod
    def get(cls, key):
        if not isinstance(key, str):
            return key
        
        mapping = {
            'PYTHON': PYTHON,
            'PYTHON_PIP': PYTHON_PIP,
        }
        return mapping.get(key.upper(), PYTHON)
    

    def to_dict(self):
        return {
            'name': self.name,
            'language': self.language,
            'parameters': self.parameters,
        }
    
    @classmethod
    def from_dict(cls, **data: dict):
        return cls(
            name=data.get('name', 'env'),
            language=data.get('language', 'python3'),
            **data.get('parameters', {})
        )









