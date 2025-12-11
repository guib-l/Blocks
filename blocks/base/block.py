import os
import io
import sys
import uuid
import json
from datetime import *
from copy import copy, deepcopy
import csv
from typing import *
from pathlib import Path
from abc import *
from .dataset import DataSet
from copy import copy, deepcopy

from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from tools.organizer import FileManager, FileError

from tools.encoder import BlockJSONEncoder

from tools.serializable import SerializableMixin

from enum import Enum







class BlockErrorType(str, Enum):
    DIRECTORY   = "Path of Block unknown"
    ORIGIN      = "Origin path of Block unknown"
    VERSION     = "Version does not match"
    LANGUAGE    = "Language not supported"


class BlockError(Exception):

    err_type = None

    def __init__(self, 
                 message: str = "Block error occurred", 
                 err_type: Optional[str] = None):
        
        self._set_error_type(err_type)

        if err_type is not None:
            message = f"{message}: Error Block : '{self.err_type}'"
        else:
            message = f"{message}: Error Block unknow"

        super().__init__(message)

    def _set_error_type(self, value):

        if value in [s.name for s in BlockErrorType]:
            self.err_type = BlockErrorType[value]
        

class Block(DataSet):

    __ntype__ = "block"
    _mandatory_attributes = []

    def __new__(cls, **kwargs):
        """
        Create a new instance of Block.
        This method ensures all parameters can be properly passed
        to Block instance creation.
        """
        for attr in cls._mandatory_attributes:
            if not hasattr(cls, attr):
                raise AttributeError(f"{cls.__name__} didn't have any {attr} method.")

        return super().__new__(cls)
    
    def __init__(self, 
                 id   = None, 
                 name = "default",
                 version = "0.0.1",
                 directory = '.',
                 authors = ["Anonymous"],
                 files = [],
                 codes = [],
                 data = {},
                 doc = None,
                 #auto_create = False,
                 **kwargs):
        """
        Initialize the BaseBlock with given options.
        Args:
            options (dict): Dictionary to be added to the block along with standard elements.
        """
        self.__name__    = None
        self.__id__      = None
        self.__version__ = None

        self.vsm = VersionManager(version)

        super().__init__(id=id,
                         name=name,
                         version=version,
                         directory=directory,
                         authors=authors,
                         files=files,
                         codes=codes,
                         data=data,
                         doc=doc,
                         **kwargs)
        


    # ===========================================
    # Properties 
    # ===========================================

    @property
    def name(self):
        """
        Get the name of the block.
        Returns:
            str: The name of the block.
        """
        return self.__name__
    
    @name.setter
    def name(self, name):
        """
        Set the name of the block.
        Args:
            name (str): The name to set for the block.
        """
        self.__name__ = name
        self._dataset['name'] = name

    @property
    def id(self):
        """
        Get the ID of the block.
        Returns:
            str: The ID of the block.
        """
        return self.__id__
        
    @id.setter
    def id(self, id=None):
        """
        Set the ID of the block.
        Args:
            id (str): The ID to set for the block.
        """

        # Valeur qui ne doit être définie qu'une seule fois
        if self.__id__ is None:

            if id is None:
                id = uuid.uuid4()
            
            if isinstance(id, str):
                if not self.is_valid_uuid(id):
                    raise ValueError("ID must be a valid valid UUID.")
                id = uuid.UUID(id)

            if not isinstance(id, uuid.UUID):
                raise ValueError("ID must be a UUID.")
            
            self.__id__ = id
            self._dataset['id'] = id
        else:
            print(f"ID is set to {self.__id__}.")
            print("It's not allowed to change it.")

    def is_valid_uuid(self, val):
        """
        Check if the given value is a valid UUID.
        Args:
            val (str): The value to check.
        Returns:
            bool: True if the value is a valid UUID, False otherwise.
        """
        try:
            _ = uuid.UUID(str(val))
            return True
        except (ValueError, AttributeError, TypeError):
            return False

    @property
    def version(self):
        """
        Get the version of the block.
        Returns:
            str: The version of the block.
        """
        return self.__version__

    @version.setter
    def version(self, version, changelog=None):
        """
        Set the version of the block.
        Args:
            version (str): The version to set for the block.
            changelog (str, optional): The changelog for the version update.
        """
        if self.vsm.current_version != version:
            self.vsm.upgrade_version(version,changelog=changelog)

        self.__version__ = self.vsm.current_version
        self._dataset['version'] = self.vsm.current_version

    @property
    def changelog(self):
        """
        Get the changelog of the block.
        Returns:
            str: The changelog of the block.
        """
        return self.vsm.changelog

    @property
    def version_info(self):
        """
        Get the version information of the block.
        Returns:
            dict: A dictionary containing the version and changelog.
        """
        return {
            "version": self.version,
            "changelog": self.changelog
        }
    
    

    # ===========================================
    # Comparisons by ID
    # ===========================================

    def __eq__(self, other):
        """
        Compare two Block instances.
        Args:
            other (Block): The other instance to compare with.
        Returns:
            bool: True if the instances are equal, False otherwise.
        """
        if not isinstance(other, Block):
            return False
        return self.id == other.id

    def __ne__(self, other):
        """
        Compare two Block instances for inequality.
        Args:
            other (Block): The other instance to compare with.
        Returns:
            bool: True if the instances are not equal, False otherwise.
        """
        if not isinstance(other, Block):
            return True
        return self.id != other.id
    
    def __hash__(self):
        """
        Generate a hash for the Block instance.
        Returns:
            int: Hash value of the instance.
        """
        return hash(self.id)
    

    # ===========================================
    # Representations
    # ===========================================

    def __str__(self):
        """
        Représentation pour les utilisateurs
        """
        return self.__repr__()

    def __repr__(self):
        """
        Représentation technique pour les développeurs
        """
        attrs = ", ".join(f"{k}={repr(v.__str__())}" for k, v in self._dataset.items() 
                      if k in ['id', 'name','version'])
        return f"{self.__class__.__name__}({attrs})" 


    # ===========================================
    # Copy object
    # ===========================================

    def copy(self):
        return type(self)(**self._dataset)

    def __copy__(self):
        return self.copy()
    
    def deepcopy(self):
        return type(self)(**deepcopy(self._dataset))
    
    def __deepcopy__(self, memo):
        return self.deepcopy()

    # ===========================================
    # Serialization
    # ===========================================


    def to_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self._dataset.keys())
        writer.writerow(self._dataset.values())
        return output.getvalue()

    def to_json(self):
        return json.dumps(self._dataset, 
                          indent=4, 
                          cls=BlockJSONEncoder)

    def to_dict(self,):
        return self._dataset


    # ===========================================
    # Versionnig
    # ===========================================


    def update_version(major=None,minor=None,patch=None):
        pass

    @abstractmethod
    def publish(self,): ...

    @abstractmethod
    def compare(self,): ...

    @abstractmethod
    def archive(self,): ...

    @abstractmethod
    def extract(self,): ...



