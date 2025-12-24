import os
import sys
import json

from typing import *
from abc import *
from pathlib import Path
from enum import Enum


from tools.serializable import SerializableMixin

from blocks.base import block
from blocks.base import BLOCK_PATH

import inspect
from typing import *



from enum import Enum
from blocks.engine.installerPy import InstallerPython,InstallerPythonWorkflow


from blocks.base.register import Register, MethodObjects

from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironMixin
from blocks.engine import PYTHON


Prototype = TypeVar('Prototype', bound='Prototype')

class INSTALLER(Enum):
    NONE     = None
    DEFAULT  = InstallerPython
    PYTHON   = InstallerPython
    WORKFLOW = InstallerPythonWorkflow





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


def Install(object,
            name=None,
            directory=None,
            installer=INSTALLER.DEFAULT):

    if directory:
        object.directory = directory
    if name:
        object.name = name

    
    object = object.__install__(name=object.name,
                       install_directory=object.directory,
                       installer=installer,)

    export_metadata(
        object,
        filename=object.__ntype__,
        format='json',
        directory=object.directory
    )







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



class Prototype(block.Block, Register):

    __ntype__ = "prototype"


    def __new__(cls, **kwargs):
        _installer   = kwargs.get('installer', INSTALLER.DEFAULT)
        _environment = kwargs.get('environment', EnvironMixin)

        if isinstance(_installer,Enum):
            _installer = _installer.value

        print('Creating Prototype class with installer:', _installer)
        print('and environment:', _environment)

        cls = type(
            cls.__name__,
            (_installer,_environment,cls),
            {}
        )
        return super().__new__(cls, **kwargs)


    def __init__(self,
                 auto_create     = False,
                 mandatory_attr  = True,
                 environment     = EnvironMixin,
                 environ_backend = PYTHON,
                 environ_arguments = {},
                 executor        = None,
                 installer       = INSTALLER.DEFAULT,
                 methods         = [],
                 files           = [],
                 allowed_name    = None,
                 **kwargs):

        # Initialisation des attributs spécifiques au Prototype
        self.mandatory_attr = mandatory_attr
            
        # Initialisation de l'environnement
        self.__init_env__(environ_backend,
                          **environ_arguments)


        # Methode destinée à l'éxécution des codes/blocks
        if executor is None:
            executor = Execute(backend='default',
                               build_backend=True)
        self.executor = executor
        
        # Enregistrement des méthodes
        # TODO: gérer les duplicatas
        # TODO: améliorer le code (refactor l'addition tableau)
        if methods + files != []:
            self.set_register_methods(methods + files, 
                                      ignore_duplicata=False)
            
        self.allowed_name = allowed_name or list(self._register_methods.keys())
        self.filter_register_methods(allowed_name=self.allowed_name)



        super().__init__(mandatory_attr = mandatory_attr,
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
             ntype=None, 
             **kwargs) -> Prototype:
        
        if not ntype:
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
            raise PrototypeErrorType(
                f"EXECUTION method failed: {e}", 'EXECUTION')


    def forward(self, name=None, **data):

        print("Executing function in Prototype forward method")
        print(f"Function name: {name}")

        with self as env:

            func   = self.get_register_methods(name=name).call
            output = func(**data)
        
        return output



    # ===========================================
    # ROOT properties
    # ===========================================

    @property
    def root(self):
        return self._root
    
    @root.setter
    def root(self, path: Optional[str] = None):
        #if path is not None:
        self._root = os.path.abspath(path)
        #elif path is None:
        #    self._root = os.path.split(path)
        #else:
        #    raise PrototypeErrorType(
        #        "Path of Node unknown", 'DIRECTORY')
        

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
                             install_directory=directory,
                             installer=installer,)
        
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













