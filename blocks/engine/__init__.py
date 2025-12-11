import os
import sys
import json

from enum import Enum

from .python_env import _empty_env,_python_env
from tools.serializable import SerializableMixin

class ExecutionError(RuntimeError):
    """Base class of error types related to Execution."""

class ExecutionSetupError(ExecutionError):
    """Execution cannot be performed with the given parameters."""

class ExecutionFailed(ExecutionError):
    """Calculation failed unexpectedly."""

class ExecutionNotFound(ExecutionError):
    """Execution not found in the given path."""

class EnvironmentError(ExecutionSetupError):
    """Raised if Execution is not properly set up with Block."""

class InputError(ExecutionSetupError):
    """Raised if inputs given to the calculator were incorrect."""

class OutputError(ExecutionSetupError):
    """Raised if inputs given to the calculator were incorrect."""


class Language(Enum):
    PYTHON   = 'python'
    R        = 'r'
    JULIA    = 'julia'
    MATLAB   = 'matlab'
    BASH     = 'bash'

    

class PYTHON(SerializableMixin):
    environment = _empty_env
    language    = Language.PYTHON
    parameters  = {}



class PYTHON_PIP(SerializableMixin):
    environment = _python_env
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












