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
from blocks.base.organizer import FileManager, FileError

from blocks.base import BLOCK_PATH

from blocks.base.encoder import BaseBlockJSONEncoder


from blocks.base.signal import Signal
from blocks.socket.interface import MESSAGE,MessageType

from enum import Enum



def _default_install(directory:str = ".",
                     **kwargs):
    ...

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

    auth_inout = [ MessageType.RESPONSE,
                   MessageType.REQUEST,
                   MessageType.DIRECT, ]
    
    default_node = {
        'interface':{
            'persistant':False,
            'restricted': False,
            'max_inp': 999,
            'max_out': 999,
        }
    }

    def __init__(self,
                 BLOCK_PATH=None,
                 INTERFACE=None,
                 ENVIRONMENT=None,
                 EXECUTOR=None,
                 **kwargs):
            
        self.__ROOT__ = None
        self.__ENV__  = None # Environnement du block
        self.__ITFC__ = None # Interface de communication
        self.__EXEC__ = None # Etat d'execution du block

        self.root = BLOCK_PATH

        super().__init__(**kwargs)

        # Methode destinée à la communication entre les node
        self.environment = ENVIRONMENT
        self.interface   = INTERFACE
        self.executor    = EXECUTOR

    @property
    def root(self):
        return self.__ROOT__
    
    @root.setter
    def root(self, path: Optional[str] = None):
        if path is not None:
            self.__ROOT__ = path
        elif path is None:
            self.__ROOT__ = os.path.split(BLOCK_PATH)
        else:
            raise NodeError("Path of Node unknown", 'DIRECTORY')
        

    # -----------------------------------------------------
    # Executor methods

    @property
    def executor(self):
        return self.__EXEC__

    @executor.setter
    def executor(self, exec = None):
        if exec is not None:
            self.__EXEC__ = exec
        else:
            raise NodeError("EXECUTOR method not provided", 'EXECUTOR')


    # -----------------------------------------------------
    # Environment methods

    @property
    def environment(self):
        return self.__ENV__
    
    @environment.setter
    def environment(self, env = None):
        if env is not None:
            self.__ENV__ = env
        else:
            raise NodeError("ENVIRONMENT method not provided", 'ENVIRONMENT')
        

    # -----------------------------------------------------
    # Interface methods

    @property
    def interface(self):
        return self.__ITFC__
    
    @interface.setter
    def interface(self, interface = None, **kwargs):
        
        intern = self.default_node['interface']
        intern.update(kwargs)
        
        if interface is not None:
            self.__ITFC__ = interface(self, **intern)
        else:
            raise NodeError("interface method not provided", 'interface')
        

    # -----------------------------------------------------
    # In / Out methods
    # Implementer une limite de nombre de message en entree et sortie
    # ainsi qu'un systeme de merge des messages
    # et de filtrage des attributs des messages

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

    def to_dict(self) -> Dict[str, Any]:
        """Convert node to dictionary representation"""
        result = super().to_dict()
        result.update({
            "root": self.root,
            "id": self.id,
            "interface": self.__ITFC__.to_dict() if self.__ITFC__ is not None else None,
            "environment": self.__ENV__ is not None,
            "executor": self.__EXEC__ is not None,
            "input_count": len(self.input) if isinstance(self.input, list) else 1 if self.input else 0,
            "output_count": len(self.output) if isinstance(self.output, list) else 1 if self.output else 0,
        })
        return result


    # -----------------------------------------------------
    # Load methods

    @classmethod
    def load(cls): ...

    # -----------------------------------------------------
    # Install methods

    @classmethod
    def install(cls, 
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

            _default_install(directory=directory,
                             **kwargs)
        return 

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

            _default_uninstall(directory=directory,
                               **kwargs)

        return cls.destroy()
    
    def destroy(self):
        """
        Destroy the block instance.
        """
        # Add any cleanup logic here if needed
        del self


    # -----------------------------------------------------
    # Build methods
    
    @abstractmethod
    def build(self,): ...


    # -----------------------------------------------------
    # Execute methods

    @abstractmethod
    def execute(self,): ... 









