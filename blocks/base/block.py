
import io
import uuid
import json
from datetime import *
from copy import copy, deepcopy
import csv
from typing import *
from abc import *
from .dataset import DataSet
from copy import copy, deepcopy

from typing import Any, Dict, Optional
from blocks.base.version import VersionManager

from tools.encoder import BlockJSONEncoder

from enum import Enum

from . import safe_operation



class BlockErrorType(str, Enum):
    DEFAULT             = "Errors occurs"
    DIRECTORY           = "Path of Block unknown"
    ORIGIN              = "Origin path of Block unknown"
    VERSION             = "Version does not match"
    INVALID_ID          = "Invalid block ID"
    MISSING_ATTRIBUTE   = "Missing mandatory attribute"
    INVALID_UUID        = "Invalid UUID format"
    ID_ALREADY_SET      = "ID has already been set and cannot be changed"
    INVALID_NAME        = "Invalid block name"
    INVALID_VERSION     = "Invalid version format"
    SERIALIZATION_ERROR = "Serialization failed"
    DESERIALIZATION_ERROR = "Deserialization failed"
    FILE_NOT_FOUND      = "File not found"
    INVALID_TYPE        = "Invalid type provided"


class BlockError(Exception):
    """Base exception for Block-related errors."""

    def __init__(self, 
                 err_type: Optional[BlockErrorType] = None,
                 message: Optional[Dict[str, Any]] = None):
        
        if err_type is not None:
            full_message = f"{err_type}\n{err_type.value}"
            if message:
                full_message += f": {message}"
            
        else:
            full_message = f"{message}: Unknown error type"

        super().__init__(full_message)







class Block(DataSet):

    __ntype__ = "block"

    _mandatory_attributes = []

    __slots__ = [
        '__name__',
        '__id__',
        '__version__',
        'vsm',
    ]

    def __new__(cls, **kwargs):
        """
        Create a new instance of Block.
        This method ensures all parameters can be properly passed
        to Block instance creation.
        """
        for attr in cls._mandatory_attributes:
            if not hasattr(cls, attr):
                raise BlockError(
                    BlockErrorType.MISSING_ATTRIBUTE,
                    f"{cls.__name__} didn't have any {attr} method."
                )

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
        if not isinstance(name, str):
            raise BlockError(
                BlockErrorType.INVALID_TYPE,
                "'name' needs to be a <string>"
            )
        if not name or name=="":
            raise BlockError(
                BlockErrorType.INVALID_NAME,
                "Invalid name : it could not be empty"
            )      

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
        # Valeur qui ne doit être définie qu'UNE seule fois
        if self.__id__ is None:

            if id is None:
                id = uuid.uuid4()
            
            if isinstance(id, str):
                if not self.is_valid_uuid(id):
                    raise BlockError(
                        BlockErrorType.INVALID_ID,
                        f'Not a valid UUID'
                    )
                
                id = uuid.UUID(id)

            if not isinstance(id, uuid.UUID):
                raise BlockError(
                    BlockErrorType.INVALID_UUID,
                    f'ID needs to be {uuid.__class__} object'
                )
            
            self.__id__ = id
            self._dataset['id'] = id

        else:
            raise BlockError(
                BlockErrorType.ID_ALREADY_SET,
                "ID has already been set and cannot be changed."
            )

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
        try:
            if self.vsm.current_version != version:
                self.vsm.upgrade_version(version,changelog=changelog)

            self.__version__ = self.vsm.current_version
            self._dataset['version'] = self.vsm.current_version

        except Exception as e:
            raise BlockError(
                BlockErrorType.VERSION,
                f"Failed to set version : {version};\nerror {e}"
            )

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

    def __repr__(self, base=''):
        """
        Représentation technique pour les développeurs
        """
        n_symb = len(self.__class__.__name__)
        space = ' ' * (n_symb+1)
        attrs = f",\n{space}".join(f"{k}={repr(v.__str__())}" for k, v in self._dataset.items() 
                      if k in ['name', 'id', 'version'])
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

        with safe_operation(
                'CSV serialisation',
                BlockErrorType.SERIALIZATION_ERROR,
                BlockError ):
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(self._dataset.keys())
            writer.writerow(self._dataset.values())
            return output.getvalue()

    def to_json(self, 
                indent=4,
                encoder=BlockJSONEncoder):

        with safe_operation(
                'JSON serialisation',
                BlockErrorType.SERIALIZATION_ERROR,
                BlockError ):
            
            return json.dumps(self._dataset, 
                              indent=indent, 
                              cls=encoder)

    def to_dict(self,):
        return self._dataset
    
    @classmethod
    def from_dict(cls, **data):
        return cls(**data)


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



