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
from typing import Protocol,Optional, Union, Callable, Iterator, BinaryIO, TextIO

from blocks.base import prototype 

from typing import Any, Dict, TypeVar, Optional
from tools.organizer import FileManager, FileError

from blocks.base import BLOCK_PATH

from tools.encoder import NodeJSONEncoder
from enum import Enum




import ast
import inspect

# TODO: inclure toutes les dependances (objets et autre)
# TODO: faire un fichier qui fait cela à l'extérieur du module Node

    

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






class NodeProtocol(Protocol):

    def forward(self, name:str|None, **data:Any)->Any:
        ...



class Node(prototype.Prototype):

    __ntype__ = "node"

    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def forward(self, name=None, **data):

        print("Executing function in Node forward method")
        print(f"Function name: {name}")

        with self as env:

            func   = self.get_register_methods(name=name).call
            output = func(**data)
        
        return output

















