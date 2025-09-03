import os,sys
import uuid
from .dataset import DataSet
from copy import copy, deepcopy

from blocks.base.baseBlock import BaseBlock
from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from blocks.base.organizer import FileManager, FileError


T = TypeVar('T', bound='Block')


default_block = {
    "id": None,
    "name": None,
    "langage": 'other',
    "location": ".",
    "description": None,
    "doc": None,
    "tags": None,
    "authors": ["Anonymous"],
    "references": None,
    "license": "MIT",
    "version": "1.0.0",
    "date": None,
}




class Block(BaseBlock):

    def __init__(self, 
                 **kwargs):
        
        super().__init__(**kwargs)

        # Serialization

        # Load / Unload

        # Copy / Past

        # Versionnning

        # Gestion fichiers

        
    

