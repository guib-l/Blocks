import os,sys
import uuid
from .dataset import DataSet
from copy import copy, deepcopy

from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from blocks.base.organizer import FileManager, FileError


T = TypeVar('T', bound='BaseBlock')


class BaseBlock(DataSet):

    _mandatory_attributes = []

    def __new__(cls, **kwargs):
        """
        Create a new instance of BaseBlock.
        This method ensures all parameters can be properly passed
        to BaseBlock instance creation.
        """
        for attr in cls._mandatory_attributes:
            if not hasattr(cls, attr):
                raise AttributeError(f"{cls.__name__} didn't have any {attr} method.")

        return super().__new__(cls)
    
    def __init__(self, 
                 id=None, 
                 name="default",
                 version=None,
                 organizer=None,
                 **kwargs):
        """
        Initialize the BaseBlock with given options.
        Args:
            options (dict): Dictionary to be added to the block along with standard elements.
        """
        self.__id__   = None 
        self.__name__ = None

        super().__init__(id=id, name=name, **kwargs)


        # Version

        # Logger

        # Files manager
   

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

    # ===========================================
    # Comparisons by ID
    # ===========================================

    def __eq__(self, other):
        """
        Compare two BaseBlock instances.
        Args:
            other (BaseBlock): The other instance to compare with.
        Returns:
            bool: True if the instances are equal, False otherwise.
        """
        if not isinstance(other, BaseBlock):
            return False
        return self.id == other.id

    def __ne__(self, other):
        """
        Compare two BaseBlock instances for inequality.
        Args:
            other (BaseBlock): The other instance to compare with.
        Returns:
            bool: True if the instances are not equal, False otherwise.
        """
        if not isinstance(other, BaseBlock):
            return True
        return self.id != other.id
    
    def __hash__(self):
        """
        Generate a hash for the BaseBlock instance.
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
                      if k in ['id', 'name'])
        return f"{self.__class__.__name__}({attrs})" 










