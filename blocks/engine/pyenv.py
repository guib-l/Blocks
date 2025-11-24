import os
import sys
import typing
import abc
import copy

from blocks.engine.pyenv import _empty_env, _python_env

class PYTHON:
    environment = _empty_env
    parameters  = {}

class PYTHON_PIP:
    environment = _python_env
    parameters  = {
        "use_shell":True,
        "directory":"."
    }




class _empty_env:

    def open(self,):
        print(f'> Open environment "Default"')

    def close(self, **kwargs):
        print(f'> Close environment "Default"')
    
    def create(self, **kwargs):
        print(f'> Create ')

    def update(self, **kwargs):
        print(f'> Update ')


from packages.manager import SelectManager


class _python_env:

    def __init__(self, 
                 package_manager=None,
                 directory=".",
                 **kwargs):
        
        self._pm = SelectManager(use_shell=True,
                                 directory=directory,
                                 manager=package_manager).manager
        

    def open(self,):
        print(f'> Open environment "Python"')

    def close(self, **kwargs):
        print(f'> Close environment "Python"')
    
    def create(self, **kwargs):
        print(f'> Create Python environment ')

    def update(self, **kwargs):
        print(f'> Update Python environment ')




