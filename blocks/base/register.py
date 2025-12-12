import os
import sys
import json

import inspect
from typing import *
from abc import *
from pathlib import Path
from enum import Enum

from dataclasses import dataclass

from tools.load import (
    _import_modules,_load_function_from_file,
    _load_callable_from_file,_load_function_with_dependencies,
    _load_function_without_decorators,save_function_to_file
)


@dataclass
class MethodObjects:
    name = ''
    ftype = None
    call = None
    directory = None 

    def __repr__(self):
        return f'{self.name}:{self.ftype}()'


class Register:
    
    _register_methods = {}
    allowed_name = None

    # ===========================================
    # Register of methods
    # ===========================================

    def get_methods(self, name=''):

        func = self.get_register_methods(name=name)
        return func.call

    def get_register_methods(self, name=''):
        # On récupère la méthode souhaité dans le registre
        # enregistré à l'instanciation
        if name=='' and len(self._register_methods)==1:
            name = list(self._register_methods.keys())[0]
            
        if name not in self._register_methods:
            raise ValueError(
                f"Method '{name}' is not registered in the method registry")

        return self._register_methods[name]

    def set_register_methods(self, 
                             defaults,
                             name_defaults=None, 
                             ignore_decorator=False,
                             ignore_duplicata=True):

        # Extract method name first to check for duplicates
        method_name = None
        if isinstance(defaults, Callable) or inspect.isfunction(defaults):
            method_name = defaults.__name__ or name_defaults
        elif isinstance(defaults, str):
            method_name = name_defaults


        if not ignore_duplicata \
                and method_name \
                and method_name in self._register_methods:
            raise ValueError(
                f"Method '{method_name}' is already registered in the method registry")

        if isinstance(defaults, Callable):
            method_obj = MethodObjects()
            method_obj.name = defaults.__name__ or name_defaults
            method_obj.ftype = type(defaults)
            method_obj.call = defaults
            method_obj.directory = None

            self._register_methods[method_obj.name] = method_obj
            return

        if inspect.isfunction(defaults):
            method_obj = MethodObjects()
            method_obj.name = defaults.__name__ or name_defaults
            method_obj.ftype = type(defaults)
            method_obj.call = defaults
            method_obj.directory = None

            self._register_methods[method_obj.name] = method_obj
            return

        if isinstance(defaults, str):
            func = _load_function_from_file(
                defaults, name_defaults,
                ignore_restriction=True
            )
            if isinstance(func,list):
                for method in func:
                    self.set_register_methods(method)
            else:
                method_obj = MethodObjects()
                method_obj.name = func.__name__ or name_defaults
                method_obj.ftype = type(func)
                method_obj.call = func
                method_obj.directory = defaults

                self._register_methods[method_obj.name] = method_obj
                return    
                
        if isinstance(defaults, list):
            for method in defaults:
                self.set_register_methods(method)

    def filter_register_methods(self,
                                allowed_name: List[str] = None):
        if allowed_name is None:
            allowed_name = self.allowed_name
        self._register_methods = {k: v for k, v in self._register_methods.items()
                                  if k in allowed_name}

    def _export(self,
                path,
                method,
                exclude_decorator=None):
        
        save_function_to_file(
            method.call,
            path,
            exclude_decorator=exclude_decorator
        )

    def export_method(self, 
                      filename: Union[str,Iterable]="",
                      destination: str=None,
                      single_file: bool=True,
                      **register):
        
        
        if not os.path.isabs(destination):
            destination = os.path.abspath(destination)

        if single_file:
            pathing = os.path.join(destination,filename)
            if os.path.exists(pathing):
                os.remove(pathing)

            for _,method in register.items():

                self._export(pathing, method, None)

        else:
            raise NotImplementedError(
                'Only Single-file feature is implemented')



    def import_method(self,
                      source: str=None, 
                      allowed_methods=None):
        
        if not os.path.isabs(source):
            source = os.path.abspath(source)

        functions = _load_function_from_file(source,None,
                                             ignore_restriction=True)
        
        self.set_register_methods(functions)

        self.filter_register_methods(allowed_name=allowed_methods or self.allowed_name)



