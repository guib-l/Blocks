import io
import sys
import uuid
import json
from datetime import *
from copy import copy, deepcopy
import csv
from typing import *
from .dataset import DataSet
from copy import copy, deepcopy

from blocks.base.version import VersionManager

from tools.encoder import BlockJSONEncoder


from blocks.utils.logger import *

from blocks.utils.exceptions import safe_operation
from blocks.utils.exceptions import BlockError,ErrorCode

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
                    message = f"{cls.__name__} didn't have any {attr} method.",
                    code=ErrorCode.BLOCK_MISSING_ATTR,
                    details={"search":attr},
                )

        return super().__new__(cls)
    
    def __init__(
            self, 
            id   = None, 
            name = "default",
            version = "0.0.1",
            directory = '.',
            authors = ["Anonymous"],
            files = [],
            codes = [],
            data = {},
            doc = None,
            stdout = sys.__stdout__,
            stderr = sys.__stderr__,
            ignore_error = True,
            **kwargs ):
        """
        Initialize the Block with given options.
        Args:
            id (str or uuid.UUID, optional): Unique identifier for the block. If None, a new UUID will be generated.
            name (str, optional): Name of the block. Defaults to "default".
            version (str, optional): Version of the block. Defaults to "0.0.1".
            directory (str, optional): Directory where the block is located. Defaults to current directory.
            authors (list of str, optional): List of authors of the block. Defaults to ["Anonymous"].
            files (list, optional): List of files associated with the block. Defaults to an empty list.
            codes (list, optional): List of code snippets associated with the block. Defaults to an empty list.
            data (dict, optional): Additional data for the block. Defaults to an empty dictionary.
            doc (str, optional): Documentation string for the block. Defaults to None.
            stdout (TextIO, optional): Stream for standard output. Defaults to sys.__stdout__.
            stderr (TextIO, optional): Stream for standard error. Defaults to sys.__stderr__.
            ignore_error (bool, optional): Whether to ignore errors during execution. Defaults to True.
            **kwargs: Additional keyword arguments for future extensions.
        
        Example:
            >>> block = Block(
            ...     name="MyBlock",
            ...     version="1.0.0",
            ...     directory="/path/to/block",
            ...     authors=["Alice", "Bob"],
            ...     files=["file1.py", "file2.py"], 
            ...     codes=["print('Hello World')"],
            ...     data={"key": "value"},
            ...     doc="This is a sample block.",
            ...     stdout=sys.stdout,
            ...     stderr=sys.stderr,
            ...     ignore_error=False
            ... )
            >>> print(block)
        
        Notes:
            - The block will automatically generate a unique ID if none is provided.
            - The version is managed using the VersionManager class, allowing for easy version upgrades and changelogs.
            - The stdout and stderr streams can be customized, and if they are logging.Logger instances, they will be wrapped in a StreamLogger for proper logging.
            - The block can be extended with additional attributes and methods in the future using **kwargs.

        """
        # Gestion stdout/stderr
        self.stdout = stdout or sys.stdout
        self.stderr = stderr or sys.stderr

        self.ignore_error = ignore_error

        self.__name__    = None
        self.__id__      = None
        self.__version__ = None

        self.vsm = VersionManager(version)

        super().__init__(
            id=id,
            name=name,
            version=version,
            directory=directory,
            authors=authors,
            files=files,
            codes=codes,
            data=data,
            doc=doc,
            **kwargs
        )


    # ===========================================
    # Propriétés stdout/stderr
    # ===========================================

    @property
    def stdout(self) -> TextIO:
        """Get the current stdout stream."""
        return sys.stdout
    
    @stdout.setter
    def stdout(self, stream: Optional[TextIO]=None):
        """Set a custom stdout stream."""

        if isinstance(stream, logging.Logger):
            stream = StreamLogger(logger=stream, 
                                  level=LOGGER_BLOCK_LEVEL)

        if not hasattr(stream, 'write'):
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_TYPE,
                message="stdout stream must have a write() method."
            )
        #self._stdout = stream 
        sys.stdout = stream
    
    @property
    def stderr(self) -> TextIO:
        """Get the current stderr stream."""
        #return self._stderr
        return sys.stderr
    
    @stderr.setter
    def stderr(self, stream: Optional[TextIO]):
        """Set a custom stderr stream."""

        if isinstance(stream, logging.Logger):
            stream = StreamLogger(logger=stream, 
                                  level=LOGGER_BLOCK_LEVEL)
            
        if not hasattr(stream, 'write'):
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_TYPE,
                message="stderr stream must have a write() method."
            )
        
        #self._stderr = stream 
        sys.stderr = stream
    
    

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
                code=ErrorCode.BLOCK_INVALID_TYPE,
                message="Name of Block needs to be a <string>"
            )
        if not name or name=="":
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_NAME,
                message="Invalid Name : it could not be empty"
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
                        code=ErrorCode.BLOCK_INVALID_ID,
                        message=f'Not a valid UUID'
                    )
                
                id = uuid.UUID(id)

            if not isinstance(id, uuid.UUID):
                raise BlockError(
                    code=ErrorCode.BLOCK_INVALID_UUID,
                    message=f'ID needs to be {uuid.__class__} object'
                )
            
            self.__id__ = id
            self._dataset['id'] = id

        else:
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_ID,
                mesage="ID has already been set and cannot be changed."
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
                code=ErrorCode.BLOCK_INVALID_VERSION,
                message=f"Failed to set version : {version};\nerror {e}"
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
                ErrorCode.BLOCK_INVALID_NAME,
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
                ErrorCode.BLOCK_INVALID_NAME,
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



