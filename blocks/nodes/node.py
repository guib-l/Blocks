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
from typing import Protocol,Optional, Union, Callable, Iterator, BinaryIO, TextIO

from blocks.base import prototype 

from typing import Any, Dict, TypeVar, Optional

from blocks.utils.logger import *

    

Node = TypeVar('Node', bound='Node')


class NodeProtocol(Protocol):

    def forward(self, name:str|None, **data:Any)->Any:
        ...

class Node(prototype.Prototype):

    __ntype__ = "node"

    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def forward(self, name=None, **data):

        logger.warning("Executing function in Workflow forward method")

        with self.environment as env:

            func   = self.get_register_methods(name=name).call
            output = func(**data)
            
        logger.warning(f"Successful Node execution")
        
        return output

















