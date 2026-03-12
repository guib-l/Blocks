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
    PluginLoader,
    save_function_to_file,
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
    
    def init_register(
            self,
            allowed_name,
            *,
            files=[],
            methods=[],
            site_packages=None,
        ):
        """
        Initialize register

        Args: 
            allowed_name ():
            files (list):
            methods (list):
            site_packages (str | None): Path to the site-packages directory of
                the virtual environment used to load file-based plugins.
                Forwarded to :class:`PluginLoader` so that dependencies of
                those plugins (e.g. numpy) are resolvable.
        """

        self._register_methods = {}
        self._plugin_loader = PluginLoader()
        self._register_site_packages = site_packages

        for _out in [methods, files]:
            self.set_register_methods(_out, ignore_duplicata=False)

        self.registred_files = files
            
        self.allowed_name = allowed_name or list(self._register_methods.keys())  

        self.filter_register_methods(allowed_name=self.allowed_name)

    # ===========================================
    # Register of methods
    # ===========================================

    def get_methods(self, name=''):

        func = self.get_register_methods(name=name)
        return func.call

    def get_register_methods(self, name=None):
        # On récupère la méthode souhaité dans le registre
        # enregistré à l'instanciation
        if (name is None) and len(self._register_methods)==1:
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
            module_name = Path(defaults).stem
            module = self._plugin_loader.load(
                module_name, defaults,
                site_packages=getattr(self, '_register_site_packages', None),
            )

            if name_defaults:
                func = getattr(module, name_defaults, None)
                if func is None:
                    raise ValueError(f"Function '{name_defaults}' not found in {defaults}")
                funcs = [func]
            else:
                funcs = [
                    obj for _, obj in inspect.getmembers(
                        module, inspect.isfunction)
                    if obj.__module__ == module_name
                ]

            for func in funcs:
                method_obj = MethodObjects()
                method_obj.name = func.__name__
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
                      source: str = None,
                      allowed_methods: list = None):

        if not os.path.isabs(source):
            source = os.path.abspath(source)

        self.set_register_methods(source)

        self.filter_register_methods(
            allowed_name=allowed_methods or self.allowed_name)

    def reload_method(self, name: str) -> None:
        """
        Reload the module that provided *name* from disk and refresh
        the corresponding entry in the register.
        """
        method = self.get_register_methods(name=name)
        if method.directory is None:
            raise ValueError(f"Method '{name}' was not loaded from a file and cannot be reloaded")

        module_name = Path(method.directory).stem
        self._plugin_loader.reload(module_name)

        # Re-register all functions from the reloaded module
        self.set_register_methods(method.directory, ignore_duplicata=True)
        self.filter_register_methods()

    def unload_method(self, name: str) -> bool:
        """
        Unload the module that provided *name* and remove it from the register.
        """
        method = self.get_register_methods(name=name)
        if method.directory is None:
            raise ValueError(f"Method '{name}' was not loaded from a file and cannot be unloaded")

        module_name = Path(method.directory).stem
        self._plugin_loader.unload(module_name)

        # Remove all methods that came from the same file
        self._register_methods = {
            k: v for k, v in self._register_methods.items()
            if v.directory != method.directory
        }
        return True



