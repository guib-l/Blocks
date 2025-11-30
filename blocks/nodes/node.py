import os
import sys
import io
import uuid
import zipfile
import json
from copy import copy, deepcopy
import csv
from typing import *
from abc import *
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable, Iterator, BinaryIO, TextIO

from ..base.dataset import DataSet
from copy import copy, deepcopy

from blocks.base.baseBlock import BaseBlock
from blocks.base import block

from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from tools.organizer import FileManager, FileError

from blocks.base import BLOCK_PATH

from tools.encoder import NodeJSONEncoder


from blocks.base.signal import Signal
from blocks.socket.interface import MESSAGE,MessageType,Interface

from enum import Enum

def _default_install(name="default-node",
                     base_directory: str = "./",
                     code_directory: str = "",
                     **kwargs):

    print(f"Installing node '{name}' in directory '{base_directory}'")

    fm = FileManager(base_directory=base_directory, auto_create=True)

    target_path = os.path.join(base_directory, name)
    #print(f"Creating node directory at: {target_path}")

    try:
        if not os.path.exists(target_path):
            os.makedirs(target_path, mode=0o755, exist_ok=True)
        else:
            os.chmod(target_path, 0o755)

    except PermissionError as e:
        raise FileError(f"Permission denied creating directory {target_path}: {e}")
    except Exception as e:
        raise FileError(f"Failed to create directory {target_path}: {e}")

    # Traitement des fichiers
    files = kwargs.get('files', [])

    for file in files:
        try:
            if os.path.isfile(file):
                if not fm.file_exists(file):
                    raise FileError(f"File {file} does not exist")
                
                dest_file = os.path.join(target_path, os.path.basename(file))
                fm.copy_files(file, dest_file, overwrite=True)
                
            elif os.path.isdir(file):
                if not fm.directory_exists(file):
                    raise FileError(f"Directory {file} does not exist")
                
                dest_dir = os.path.join(target_path, os.path.basename(file))
                fm.copy_files(file, dest_dir, overwrite=True)
                
            else:
                print(f"Warning: {file} is neither a file nor a directory")
                
        except Exception as e:
            print(f"Error processing file {file}: {e}")
            raise FileError(f"Failed to process file {file}: {e}")

    return target_path




def _default_uninstall(directory:str = ".",
                          **kwargs):
    ...







Node = TypeVar('Node', bound='Node')



class NodeErrorType(str, Enum):
    INPUT       = "Wrong input"
    OUTPUT      = "Wrong output"
    PROCESSING  = "Node is being processed"
    INSTALLER   = "Installer method failed"
    UNINSTALLER = "Uninstaller method failed"
    LOADING     = "Loading method failed"
    SAVING      = "Saving method failed"
    BUILD       = "Build method failed"
    EXECUTION   = "Execution method failed"
    DESTINATION = "Destination of Node unknown"
    DIRECTORY   = "Path of Node unknown"
    INTERFACE   = "Interface method not provided"
    UNKNOWN     = "Unknown error"



class NodeError(Exception):

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

        if value in [s.name for s in NodeErrorType]:
            self.err_type = NodeErrorType[value]


class Node(block.Block):

    __ntype__ = "node"

    def __init__(self,
                 auto            = True,
                 _mandatory_attr = True,
                 _environment    = None,
                 _executor       = None,
                 **kwargs):

        # Initialisation des attributs spécifiques au Node
        self._mandatory_attr = _mandatory_attr
            
        #self.root = _block_path

        # Methode destinée à la communication entre les node
        self.environment = _environment
        self.executor    = _executor

        super().__init__(_mandatory_attr=_mandatory_attr,
                         _environment=self.environment,
                         _executor=self.executor,
                         **kwargs)
        
        if auto and self._executor:
            self.build()

    # -----------------------------------------------------
    # Build methods
    
    def build(self, *args, **kwargs): 

        try:
            self.executor.build_backend(*args, **kwargs)
        except Exception as e:
            raise NodeError(f"BUILD method failed: {e}", 'BUILD')


    # -----------------------------------------------------
    # Execute methods
        
    def execute(self, **data):
        
        forward = getattr(self, 'forward', None)

        try:
            exec = self.executor.execute(forward=forward)
            return exec(**data)

        except Exception as e:
            raise NodeError(f"EXECUTION method failed: {e}", 'EXECUTION')


    def forward(self, name=None, **data):

        print("Executing function in Node forward method")

        with self.environment as env:

            func   = env.get_functions(name=name)
            output = func(**data)
        
        return output


    # -----------------------------------------------------
    # Load methods

    @classmethod
    def load(cls,
             name:str,
             directory=BLOCK_PATH,
             **kwargs) -> Node:
        
        data = json.load(
            open(os.path.join(directory, name, 'blocks.json')))
        data.update(kwargs) 

        return cls(_build=False, **data)


    # -----------------------------------------------------

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
            raise NodeError("Path of Node unknown", 'DIRECTORY')
        

    # -----------------------------------------------------
    # Executor methods

    @property
    def _executor(self):
        return self.__EXEC__

    @_executor.setter
    def _executor(self, exec = None):

        if exec is None and self._mandatory_attr:
            raise NodeError("EXECUTOR method not provided", 'EXECUTOR')

        self.__EXEC__ = exec    
                

    # -----------------------------------------------------
    # Environment methods

    @property
    def _environment(self):
        return self.__ENV__

    @_environment.setter
    def _environment(self, env = None):
        
        if env is None and self._mandatory_attr:
            raise NodeError("ENVIRONMENT method not provided", 'ENVIRONMENT')

        self.__ENV__ = env
        

    # -----------------------------------------------------
    # Message methods

    def error(self, e, err): 
        return MESSAGE.generate_error(
            self,
            subject=f"Error on node {self.id}",
            error_info={"error_type":e,"message":err},
        )

    def info(self, info='Information'): 
        return MESSAGE.generate_info(
            self,
            subject=f"Information on node {self.id}",
            info=info
        )

    # -----------------------------------------------------
    # Serialization methods

    def to_json(self):
        return json.dumps(self._dataset, 
                          indent=4, 
                          cls=NodeJSONEncoder)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation"""
        result = super().to_dict()
        result.update({
            "root": self.root,
            "id": self.id,
            #"interface": self.__ITFC__.to_dict() if self.__ITFC__ is not None else None,
            "environment": self.__ENV__.to_dict() is not None,
            "executor": self.__EXEC__.to_dict() is not None,
            #"input_count": len(self.input) if isinstance(self.input, list) else 1 if self.input else 0,
            #"output_count": len(self.output) if isinstance(self.output, list) else 1 if self.output else 0,
        })
        return result

    # -----------------------------------------------------
    # Install methods

    @classmethod
    def install(cls, 
                name="default-node",
                installer = None,
                directory:str = ".",
                **kwargs):
        """
        Install the block in the given path.
        Args:
            path (str): Path to install the block.
        """
        if installer is not None:
            try:
                installer(directory=directory,
                          **kwargs)
            except Exception as e:
                
                raise NodeError("INSTALLER method failed", 'INSTALLER')
        else:
            _default_install(name=name,
                             base_directory=directory,
                             **kwargs)
        return cls(name=name,
                   path=directory,
                   _build=kwargs.get('_build',True),
                   **kwargs)

    @classmethod
    def uninstall(cls,
                  uninstaller = None,
                  directory:str = ".",
                  **kwargs):
        """
        Uninstall the block from the given path.
        """

        if uninstaller is not None:
            try:
                uninstaller(directory=directory,
                            **kwargs)
            except Exception as e:
                raise NodeError("UNINSTALLER method failed", 'UNINSTALLER')
        else:

            _default_uninstall(base_directory=directory,
                               **kwargs)

        return cls.destroy()
    
    def destroy(self):
        """
        Destroy the block instance.
        """
        # Add any cleanup logic here if needed
        del self












    # -----------------------------------------------------
    # Interface methods
    """
    @property
    def interface(self):
        return self.__ITFC__
    
    @interface.setter
    def interface(self, _interface = None):
        if _interface is None and self._mandatory_attr:
            raise NodeError("interface method not provided", 'interface')
        
        from blocks.socket.interface import Interface

        if isinstance(_interface, Interface):
            self.__ITFC__ = _interface
            return
        elif isinstance(_interface, dict):
            self.__ITFC__ = Interface.from_dict(**_interface)
            return
        else:
            intern = self.default_node['interface']
            if _interface is not Interface:
                _interface = Interface

            self.__ITFC__ = _interface(self,
                                       environment = self.environment,
                                       executor    = self.executor, 
                                       **intern)
    """

    # -----------------------------------------------------
    # In / Out methods
    # Implementer une limite de nombre de message en entree et sortie
    # ainsi qu'un systeme de merge des messages
    # et de filtrage des attributs des messages

    """
    @property
    def input(self): 
        return self.__ITFC__.register
    
    @input.setter
    def input(self, msg, value=None, index=-1):
        if isinstance(msg, MESSAGE):
            if msg.TYPE in self.auth_inout:
                self.__ITFC__.receive(msg)
            else:
                txt = f"Incorrect input type : {msg.TYPE}. \nAuthorized types are {self.auth_inout}"
                raise NodeError(txt, "input")
            
        elif isinstance(msg,str):
            self.__ITFC__.provide(msg, value, index)
        else:
            raise NodeError("Incorrect input type","input")

    @property
    def output(self): 
        return self.__ITFC__.outputs

    """
