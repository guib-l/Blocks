import os
import sys
import json

from typing import *
from abc import *
from pathlib import Path
from enum import Enum

from dataclasses import dataclass

from tools.serializable import SerializableMixin

from blocks.base import block
from blocks.base import BLOCK_PATH

import inspect
from typing import *

Prototype = TypeVar('Prototype', bound='Prototype')


from tools.load import (
    _import_modules,_load_function_from_file,
    _load_callable_from_file,_load_function_with_dependencies,
    _load_function_without_decorators,save_function_to_file
)


from enum import Enum
from blocks.engine.python_install import _python_installer




class INSTALLER(Enum):
    NONE    = None
    DEFAULT = _python_installer
    PYTHON  = _python_installer





def export_metadata(block: Prototype, 
                    filename: str,
                    format: str = 'json',
                    directory: str = None, ) -> None:
    """
    Export metadata from a Block instance to a file.
    Args:
        block (Block): The Block instance to export metadata from.
        filename (str): The name of the file to export to (without extension).
        format (str): The format to export the metadata in ('json', 'csv', etc.).
    """
    if os.path.splitext(filename)[1] != '':
        if os.path.splitext(filename)[1] != f".{format}":
            raise ValueError("Le nom de fichier doit se terminer par " \
"l'extension correspondant au format spécifié.")    
        
    content = None
    if format == 'json':
        content = block.to_json()
    elif format == 'csv':
        content = block.to_csv()
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    if content:
        path = os.path.join(directory or block.directory,
                            block.name,
                            f"{filename}.{format}")

        with open(path, "w") as f:
            f.write(content)




class PrototypeErrorType(str, Enum):
    PROCESSING  = "Prototype is being processed"
    INSTALLER   = "Installer method failed"
    UNINSTALLER = "Uninstaller method failed"
    LOADING     = "Loading method failed"
    SAVING      = "Saving method failed"
    BUILD       = "Build method failed"
    EXECUTION   = "Execution method failed"
    DIRECTORY   = "Path of Prototype unknown"
    UNKNOWN     = "Unknown error"


class PrototypeError(Exception):

    err_type = None

    def __init__(self, 
                 message: str = "Node error occurred", 
                 err_type: Optional[str] = None):

        self._set_error_type(err_type)

        if err_type is not None:
            message = f"{message}: Error Node : '{self.err_type}'"
        else:
            message = f"{message}: Error Node unknow"

        super().__init__(message)

    def _set_error_type(self, value):

        if value in [s.name for s in PrototypeErrorType]:
            self.err_type = PrototypeErrorType[value]



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

    def get_register_methods(self, name=''):
        # On récupère la méthode souhaité dans le registre
        # enregistré à l'instanciation

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
                      source: str=None):
        
        if not os.path.isabs(source):
            source = os.path.abspath(source)

        functions = _load_function_from_file(source,None,
                                             ignore_restriction=True)
        
        self.set_register_methods(functions)
        self.filter_register_methods(allowed_name=self.allowed_name)


class Prototype(block.Block, Register):

    __ntype__ = "prototype"


    def __new__(cls, **kwargs):
        _installer = kwargs.get('installer', INSTALLER.DEFAULT)

        if isinstance(_installer,Enum):
            _installer = _installer.value

        if _installer is not None:
            _cls = type(
                cls.__name__,
                (_installer,cls),
                {}
            )
        return super().__new__(_cls)


    def __init__(self,
                 auto_create    = False,
                 mandatory_attr = True,
                 environment    = None,
                 executor       = None,
                 installer      = INSTALLER.DEFAULT,
                 methods        = [],
                 files          = [],
                 allowed_name   = None,
                 **kwargs):

        # Initialisation des attributs spécifiques au Prototype
        self.mandatory_attr = mandatory_attr
            
        # Methode destinée à la communication entre les Prototype
        self.environment = environment
        self.executor    = executor

        # Enregistrement des méthodes
        # TODO: gérer les duplicatas
        # TODO: améliorer le code (refactor addition tableau)
        if methods + files != []:
            self.set_register_methods(methods + files, 
                                      ignore_duplicata=False)
        self.allowed_name = allowed_name or self._register_methods.keys()
        self.filter_register_methods(allowed_name=self.allowed_name)


        super().__init__(mandatory_attr = mandatory_attr,
                         #auto_create = auto_create,
                         allowed_name = self.allowed_name,
                         **kwargs)
        
        if hasattr(self,'__post_init__'):
            self.__post_init__(name=self.name,
                               directory=self.directory,
                               auto_create=auto_create)
    



    # ===========================================
    # Load methods
    # ===========================================

    @classmethod
    def load(cls,
             name:str,
             directory=BLOCK_PATH,
             format='json',
             **kwargs) -> Prototype:
        
        ntype = cls.__ntype__
        origin = os.path.join(
            os.path.abspath(directory), name, ntype + f'.{format}')
        
        data = json.load( open(origin))
        data.update(kwargs)

        if kwargs.get('auto_create') is not None:
            return cls(auto_create=kwargs.get('auto_create'),
                       **data)
        return cls(auto_create=False, **data)


    @classmethod
    def load_from_dict(cls, data):
        obj = cls(**data)
        return obj

    @classmethod
    def load_from_directory(cls, 
                            name=None,
                            path=None,
                            ntype=None,
                            format='json',
                            encoding='utf-8',
                            **kwargs):
        import json
        if ntype is None:
            ntype = cls.__ntype__

        path = os.path.abspath(path)
        full_path = os.path.join(path, name, 
                                 ntype + f'.{format}')

        with open(full_path, 'r', encoding=encoding) as file:
            content = file.read()

        data = json.loads(content)

        data.update(kwargs)

        obj = cls(**data)
        return obj
    
    # ===========================================
    # Execute methods
    # ===========================================
        
    def execute(self, **data):
        
        forward = getattr(self, 'forward', None)

        try:
            exec = self.executor.execute(forward=forward)
            return exec(**data)

        except Exception as e:
            raise PrototypeErrorType(f"EXECUTION method failed: {e}", 'EXECUTION')


    def forward(self, name=None, **data):

        print("Executing function in Node forward method")

        with self.environment as env:

            func   = env.get_functions(name=name)
            output = func(**data)
        
        return output



    # ===========================================
    # ROOT properties
    # ===========================================

    @property
    def root(self):
        return self.__ROOT__
    
    @root.setter
    def root(self, path: Optional[str] = None):
        if path is not None:
            self.__ROOT__ = path
        elif path is None:
            self.__ROOT__ = os.path.split(path)
        else:
            raise PrototypeErrorType(
                "Path of Node unknown", 'DIRECTORY')
        

    # ===========================================
    # Execution properties
    # ===========================================

    @property
    def executor(self):
        return self.__EXEC__

    @executor.setter
    def executor(self, exec = None):

        if exec is None and self.mandatory_attr:
            raise PrototypeErrorType(
                "EXECUTOR method not provided", 'EXECUTOR')

        self.__EXEC__ = exec    
                
    # ===========================================
    # Environment properties
    # ===========================================

    @property
    def environment(self):
        return self.__ENV__

    @environment.setter
    def environment(self, env = None):
        
        if env is None and self.mandatory_attr:
            raise PrototypeErrorType(
                "ENVIRONMENT method not provided", 'ENVIRONMENT')

        self.__ENV__ = env





    # ===========================================
    # Installater / Uninstaller
    # ===========================================

    @classmethod
    def install(cls, 
                name="default-node",
                installer = INSTALLER.DEFAULT,
                directory:str = ".",
                codes:List = [],
                files:List[str] = [],
                **kwargs):
        """
        Install the block in the given path.
        Args:
            path (str): Path to install the block.
        """
        if 'auto_create' in kwargs:
            del kwargs['auto_create']

        instance =  cls(name=name,
                        directory=directory,
                        auto_create=True,
                        **kwargs )
        
        if instance is None:
            raise PrototypeErrorType(
                "Installation of Prototype failed", 'INSTALLER')
        

        instance.__install__(name=name,
                             directory=directory,
                             installer=installer,
                             files=files,
                             codes=codes,)
        
        export_metadata(
            instance,
            filename=instance.__ntype__,
            format='json',
            directory=instance.directory
        )
        return instance

    def uninstall(self,):

        self.__uninstall__()
        
        return None













