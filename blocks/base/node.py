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

from .dataset import DataSet
from copy import copy, deepcopy

from blocks.base.baseBlock import BaseBlock
from blocks.base.block import Block

from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from blocks.base.organizer import FileManager, FileError

from blocks.base import BLOCK_PATH

from blocks.base.encoder import BaseBlockJSONEncoder


from blocks.base.signal import Signal

from enum import Enum



def _default_install(directory:str = ".",
                     **kwargs):
    ...

def _default_uninstall(directory:str = ".",
                          **kwargs):
    ...



T = TypeVar('T', bound='Node')



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


class Node(Block):

    __ROOT__ = None
    __ENV__  = None # Environnement du block
    __ITFC__ = None # Interface de communication 

    def __init__(self,
                 BLOCK_PATH=None,
                 INTERFACE=None,
                 ENVIRONMENT=None,
                 **kwargs):
        
        self.root = BLOCK_PATH

        super().__init__(**kwargs)

        # Methode destinée à la communication entre les node
        self.environment = ENVIRONMENT
        self.interface   = INTERFACE
        

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
        if interface is not None:
            self.__ITFC__ = interface(self, **kwargs)
        else:
            raise NodeError("interface method not provided", 'interface')
        

    @property
    def input(self): 
        return self.__ITFC__.input

    @property
    def output(self): 
        return self.__ITFC__.output

    @property
    def error(self): 
        return self.__ITFC__.error

    @property
    def info(self): 
        return self.__ITFC__.input


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

    @abstractmethod
    def move_to(self,): ...

    # -----------------------------------------------------
    # Build methods
    
    @abstractmethod
    def build(self,): ...

    # -----------------------------------------------------
    # Execute methods

    @abstractmethod
    def execute(self,): ...









