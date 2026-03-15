
import io
import sys
import uuid
import json
from datetime import *
from copy import deepcopy
import csv
from typing import *
from abc import abstractmethod

from .dataset import DataSet

from blocks.base.version import VersionManager

from tools.encoder import BlockJSONEncoder


from blocks.utils.logger import *

from blocks.utils.exceptions import safe_operation
from blocks.utils.exceptions import BlockError,ErrorCode

class Block(DataSet):
    """Base class for Blocks.

    A `Block` is a versioned dataset-like object that can be serialized and
    executed within the Blocks engine.

    Attributes:
        __ntype__ (str): Object type marker used by the framework.
        _mandatory_attributes (list[str]): Method names required on subclasses.

    Notes:
        This class uses `__slots__` for a smaller memory footprint.
    """

    __ntype__ = "block"

    _mandatory_attributes = []

    __slots__ = [
        'ignore_error',
        '__name__',
        '__id__',
        '__version__',
        'vsm',
    ]

    def __new__(cls, **kwargs):
        """Create a new instance of `Block`.

        This hook validates that required subclass methods exist before the
        instance is created.

        Args:
            **kwargs: Ignored. Present to support a flexible construction API.

        Raises:
            BlockError: If one of the required methods declared in
                `_mandatory_attributes` is missing on the subclass.

        Returns:
            Block: A newly allocated instance.
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
            id: Union[str, uuid.UUID, None]= None, 
            name: str = "default",
            version: str = "0.0.1",
            directory: str = '.',
            authors: list = ["Anonymous"],
            files: list = [],
            codes: list = [],
            data: dict = {},
            doc: Optional[str] = None,
            stdout: Optional[TextIO] = sys.__stdout__,
            stderr: Optional[TextIO] = sys.__stderr__,
            ignore_error: bool = True,
            **kwargs ):
        """
        Initialize a `Block`.

        Args:
            id (str | uuid.UUID | None): Unique identifier for the block. If
                `None`, a new UUID is generated.
            name (str): Block name.
            version (str): Semantic version string.
            directory (str): Block directory.
            authors (list[str]): Block authors.
            files (list[str]): Files associated with the block.
            codes (list): Code snippets associated with the block.
            data (dict): Additional data payload.
            doc (str | None): Documentation string.
            stdout (TextIO): Stream to use as `sys.stdout` during the block
                lifetime.
            stderr (TextIO): Stream to use as `sys.stderr` during the block
                lifetime.
            ignore_error (bool): Whether to ignore errors during execution.
            **kwargs: Additional keyword arguments forwarded to `DataSet`.

        Raises:
            BlockError: If `name`, `id`, `stdout`, `stderr`, or `version` are
                invalid.

        Example:
            >>> block = Block(name="MyBlock", version="1.0.0")
            >>> block.name
            'MyBlock'
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
        """Current stdout stream.

        Returns:
            TextIO: The current `sys.stdout`.
        """
        return sys.stdout
    
    @stdout.setter
    def stdout(self, stream: Union[TextIO, 'logging.Logger', None] = None):
        """Set a custom stdout stream.

        If `stream` is a `logging.Logger`, it will be wrapped in a
        :class:`~blocks.utils.logger.StreamLogger`.

        Args:
            stream (TextIO | logging.Logger | None): A stream-like object with a
                `write()` method.

        Raises:
            BlockError: If `stream` does not provide a `write()` method.
        """

        if isinstance(stream, logging.Logger):
            stream = StreamLogger(logger=stream,   # type: ignore[assignment]
                                  level=LOGGER_BLOCK_LEVEL)

        if not hasattr(stream, 'write'):
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_TYPE,
                message="stdout stream must have a write() method."
            )
        #self._stdout = stream 
        sys.stdout = stream  # type: ignore[assignment]
    
    @property
    def stderr(self) -> TextIO:
        """Current stderr stream.

        Returns:
            TextIO: The current `sys.stderr`.
        """
        #return self._stderr
        return sys.stderr
    
    @stderr.setter
    def stderr(self, stream: Union[TextIO, 'logging.Logger', None] = None):
        """Set a custom stderr stream.

        If `stream` is a `logging.Logger`, it will be wrapped in a
        :class:`~blocks.utils.logger.StreamLogger`.

        Args:
            stream (TextIO | logging.Logger): A stream-like object with a
                `write()` method.

        Raises:
            BlockError: If `stream` does not provide a `write()` method.
        """

        if isinstance(stream, logging.Logger):
            stream = StreamLogger(logger=stream,   # type: ignore[assignment]
                                  level=LOGGER_BLOCK_LEVEL)
            
        if not hasattr(stream, 'write'):
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_TYPE,
                message="stderr stream must have a write() method."
            )
        
        #self._stderr = stream 
        sys.stderr = stream  # type: ignore[assignment]
    
    

    # ===========================================
    # Properties 
    # ===========================================

    @property
    def name(self):
        """Block name.

        Returns:
            str: The name of the block.
        """
        return self.__name__
    
    @name.setter
    def name(self, name):
        """Set the block name.

        Args:
            name (str): The name to set.

        Raises:
            BlockError: If `name` is not a non-empty string.
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
        """Block UUID.

        Returns:
            uuid.UUID: The block identifier.
        """
        return self.__id__
        
    @id.setter
    def id(self, id=None):
        """Set the block UUID (write-once).

        Args:
            id (str | uuid.UUID | None): Identifier to set. If `None`, a new
                UUID is generated.

        Raises:
            BlockError: If `id` is invalid, or if the ID has already been set.
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
                    message=f'ID needs to be {uuid.UUID} object'
                )
            
            self.__id__ = id
            self._dataset['id'] = id

        else:
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_ID,
                message="ID has already been set and cannot be changed."
            )

    def is_valid_uuid(self, val):
        """Return True if `val` can be parsed as a UUID.

        Args:
            val (Any): Value to validate.

        Returns:
            bool: `True` if UUID-like, `False` otherwise.
        """
        try:
            _ = uuid.UUID(str(val))
            return True
        except (ValueError, AttributeError, TypeError):
            return False
        
    # ===========================================
    # Versioning
    # ===========================================

    @property
    def version(self):
        """Current block version.

        Returns:
            str: The version string.
        """
        return self.__version__

    @version.setter
    def version(self, version, changelog=None):
        """Set the block version.

        This delegates version transitions to `VersionManager`.

        Args:
            version (str): Target version.
            changelog (str | None): Optional changelog message.

        Raises:
            BlockError: If version upgrade fails.
        """
        try:
            if self.vsm.current_version != version:
                self.vsm.upgrade_version(version, changelog=changelog or "")

            self.__version__ = self.vsm.current_version
            self._dataset['version'] = self.vsm.current_version

        except Exception as e:
            raise BlockError(
                code=ErrorCode.BLOCK_INVALID_VERSION,
                message=f"Failed to set version : {version};\nerror {e}"
            )

    @property
    def changelog(self):
        """Version changelog.

        Returns:
            str: Changelog text.
        """
        return self.vsm.get_changelog()

    @property
    def version_info(self):
        """Return a serializable version summary.

        Returns:
            dict: A dictionary containing `version` and `changelog`.
        """
        return {
            "version": self.version,
            "changelog": self.changelog
        }
    
    

    # ===========================================
    # Comparisons by ID
    # ===========================================

    def __eq__(self, other):
        """Return True when two blocks share the same UUID.

        Args:
            other (Any): Value to compare.

        Returns:
            bool: Equality result.
        """
        if not isinstance(other, Block):
            return False
        return self.id == other.id

    def __ne__(self, other):
        """Return True when blocks do not share the same UUID.

        Args:
            other (Any): Value to compare.

        Returns:
            bool: Inequality result.
        """
        if not isinstance(other, Block):
            return True
        return self.id != other.id
    
    def __hash__(self):
        """Hash based on the block UUID.

        Returns:
            int: Hash value.
        """
        return hash(self.id)
    

    # ===========================================
    # Representations
    # ===========================================

    def __str__(self):
        """User-facing string representation."""
        return self.__repr__()

    def __repr__(self, base=''):
        """Developer-facing representation."""
        n_symb = len(self.__class__.__name__ or '')
        space = ' ' * (n_symb+1)
        attrs = f",\n{space}".join(f"{k}={repr(v.__str__())}" for k, v in self._dataset.items() 
                      if k in ['name', 'id', 'version'])
        return f"{self.__class__.__name__}({attrs})" 


    # ===========================================
    # Copy object
    # ===========================================

    def copy(self):
        """Shallow copy the block.

        Returns:
            Block: A new instance with the same dataset values.
        """
        return type(self)(**self._dataset)

    def __copy__(self):
        return self.copy()
    
    def deepcopy(self):
        """Deep copy the block.

        Returns:
            Block: A new instance with a deep-copied dataset.
        """
        return type(self)(**deepcopy(self._dataset))
    
    def __deepcopy__(self, memo):
        return self.deepcopy()

    # ===========================================
    # Serialization
    # ===========================================


    def to_csv(self, filepath: str = '', delimiter: str = ',') -> str:
        """Serialize the block dataset as a single-row CSV.

        Returns:
            str: CSV content with a header row and a single value row.

        Raises:
            BlockError: If serialization fails.
        """

        with safe_operation(
                'CSV serialisation',
                ErrorCode.BLOCK_INVALID_NAME,
                ERROR=BlockError ):
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(self._dataset.keys())
            writer.writerow(self._dataset.values())
            return output.getvalue()

    def to_json(self,
                encoder: Type[json.JSONEncoder] = BlockJSONEncoder,
                indent: int = 4):
        """Serialize the block dataset as JSON.

        Args:
            indent (int): Indentation passed to `json.dumps`.
            encoder (type[json.JSONEncoder]): Encoder class.

        Returns:
            str: JSON string representation.

        Raises:
            BlockError: If serialization fails.
        """

        with safe_operation(
                'JSON serialisation',
                ErrorCode.BLOCK_INVALID_NAME,
                ERROR=BlockError ):
            
            return json.dumps(self._dataset, 
                              indent=indent, 
                              cls=encoder)

    def to_dict(self,):
        """Return the underlying dataset mapping.

        Returns:
            dict: Internal dataset representation.
        """
        return self._dataset
    
    @classmethod
    def from_dict(cls, **data):
        """Create a `Block` from a dictionary payload.

        Args:
            **data: Keyword arguments forwarded to the constructor.

        Returns:
            Block: A new instance.
        """
        return cls(**data)


    # ===========================================
    # Versionnig
    # ===========================================


    def update_version(self, major=None, minor=None, patch=None):
        pass

    @abstractmethod
    def publish(self,): ...

    @abstractmethod
    def compare(self,): ...

    @abstractmethod
    def archive(self,): ...

    @abstractmethod
    def extract(self,): ...



