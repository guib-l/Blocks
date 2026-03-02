# blocks/utils/exceptions.py
from typing import Any, Dict, Optional
import json

from enum import Enum
from contextlib import contextmanager

from blocks.utils.logger import *

import importlib

def optional_import(module_name):
    try:
        return importlib.import_module(module_name)
    except ImportError:
        return None


@contextmanager
def safe_operation(
        operation_name: str, 
        code=None,
        details={},
        ERROR=None ):
    """
    Context manager pour encapsuler des opérations critiques.
    Capture toutes les exceptions non-Block et les convertit en BlockError.
    """
    try:
        yield  
    except ERROR:
        raise
    except Exception as e:
        message = f"Unexpected error during {operation_name}"
        logger.critical(message, extra=details)
        raise ERROR(
            code=code,
            message=message,
            details=details,
            cause=e
        ) from e


# ==============================================
# Blocks related errors
# ==============================================


class ErrorCode(str,Enum):
    BLOCK_INVALID = 'BLOCK_1000'
    BLOCK_INVALID_ID = 'BLOCK_1001'
    BLOCK_INVALID_UUID = 'BLOCK_1002'
    BLOCK_INVALID_NAME = 'BLOCK_1003'
    BLOCK_INVALID_TYPE = 'BLOCK_1004'
    BLOCK_INVALID_VERSION = 'BLOCK_1005'
    BLOCK_SERIALIZE_ERR = 'BLOCK_1006'
    BLOCK_DESERIALIZE_ERR = 'BLOCK_1007'
    BLOCK_MISSING_ATTR = 'BLOCK_1008'

    PROTOTYPE_INVALID = 'PROTOTYPE_1000'
    PROTOTYPE_INIT_EXECUTOR = 'PROTOTYPE_1001'
    PROTOTYPE_INIT_REGISTER = 'PROTOTYPE_1002'
    PROTOTYPE_INIT_ENVIRONMENT = 'PROTOTYPE_1003'
    PROTOTYPE_INIT_INSTALLER = 'PROTOTYPE_1004'
    PROTOTYPE_INSTALLER_ERR = 'PROTOTYPE_1005'
    PROTOTYPE_UNINSTALLER_ERR = 'PROTOTYPE_1006'
    PROTOTYPE_LOADING_ERR = 'PROTOTYPE_1007'
    PROTOTYPE_EXECUTION = 'PROTOTYPE_1008'
    PROTOTYPE_SERIALIZE_ERR = 'PROTOTYPE_1009'
    PROTOTYPE_DESERIALIZE_ERR = 'PROTOTYPE_1010'

    NODE_INVALID = 'NODE_1000'
    NODE_EXECUTION = 'NODE_1001'

    WORKFLOW_INVALID = 'WORKFLOW_1000'
    WORKFLOW_ERROR_TYPE = 'WORKFLOW_1001'
    WORKFLOW_INIT_EXECUTOR = 'WORKFLOW_1001'
    WORKFLOW_INIT_REGISTER = 'WORKFLOW_1002'
    WORKFLOW_INIT_ENVIRONMENT = 'WORKFLOW_1003'
    WORKFLOW_INIT_INSTALLER = 'WORKFLOW_1004'
    WORKFLOW_INSTALLER_ERR = 'WORKFLOW_1005'
    WORKFLOW_UNINSTALLER_ERR = 'WORKFLOW_1006'
    WORKFLOW_IMPORT_NODES = 'WORKFLOW_1007'
    WORKFLOW_LOADING_ERR = 'WORKFLOW_1007'
    WORKFLOW_CREATING_ERR = 'WORKFLOW_1007'
    WORKFLOW_EXECUTION = 'WORKFLOW_1008'
    WORKFLOW_REGISTER = 'WORKFLOW_1009'
    WORKFLOW_COMMUNICATE = 'WORKFLOW_1010'
    WORKFLOW_SERIALIZE_ERR = 'WORKFLOW_1009'
    WORKFLOW_DESERIALIZE_ERR = 'WORKFLOW_1010'
    WORKFLOW_APPLY_TRANSFORMER = 'WORKFLOW_1010'




class BaseError(Exception):

    code = None

    def __init__(
            self, 
            message:str,
            code:Optional[ErrorCode]=None,
            details:Optional[Dict[str,Any]]=None,
            cause: Optional[Exception]=None
        ):
        self.message = message
        self.code = code or self.code
        self.details = details or {}

        super().__init__(message)

        if cause:
            self.__cause__ = cause

    def to_dict(self):
        return {
            'error':self.__class__.__name__,
            'code':self.code,
            'message':self.message,
            'details':self.details
        }
    
    def __repr__(self):
        return f"{self.__class__.__name__}(code={self.code}, message={self.message!r}, details={self.details})"



class BlockError(BaseError):
    """Exception for Block-related errors."""
    code = ErrorCode.BLOCK_INVALID

class PrototypeError(BaseError):
    """Exception for Block-related errors."""
    code = ErrorCode.PROTOTYPE_INVALID

class NodeError(BaseError):
    """Exception for Block-related errors."""
    code = ErrorCode.NODE_INVALID

class WorkflowError(BaseError):
    """Exception for Block-related errors."""
    code = ErrorCode.WORKFLOW_INVALID




# ==============================================
# Execution related errors
# ==============================================


class ErrorCodeExec(str,Enum):
    EXECUTE_ERROR = 'EXECUTE_1000'
    EXECUTE_ERROR_INIT = 'EXECUTE_1000'
    EXECUTE_ERROR_SERIALIZATION = 'EXECUTE_1000'
    EXECUTE_ERROR_DESERIALIZATION = 'EXECUTE_1000'
    EXECUTE_ERROR_BUILD = 'EXECUTE_1000'
    EXECUTE_ERROR_RUN = 'EXECUTE_1000'
    EXECUTE_ERROR_IMPLEMENT = 'EXECUTE_1000'

class ExecutionError(BaseError):
    """Execution not found in the given path."""
    code = ErrorCodeExec.EXECUTE_ERROR

class ExecutionSetupError(BaseError):
    """Execution cannot be performed with the given parameters."""
    code = ErrorCodeExec.EXECUTE_ERROR_INIT

class ExecutionFailed(BaseError):
    """Calculation failed unexpectedly."""
    code = ErrorCodeExec.EXECUTE_ERROR_RUN




# ==============================================
# Environment related errors
# ==============================================


class ErrorCodeEnv(str,Enum):
    ENV_ERROR = 'ENV_1001'
    ENV_ERROR_INIT = 'ENV_1001'
    ENV_ERROR_SERIALIZATION = 'ENV_1001'
    ENV_ERROR_DESERIALIZATION = 'ENV_1001'
    ENV_ERROR_BUILD = 'ENV_1001'
    ENV_ERROR_RUN = 'ENV_1001'
    ENV_ERROR_UPDATE = 'ENV_1001'
    ENV_ERROR_ENTER = 'ENV_1001'
    ENV_ERROR_CLOSE = 'ENV_1001'
    ENV_ERROR_IMPLEMENT = 'ENV_1001'
    ENV_ERROR_DIFF = 'ENV_1001'

class EnvironmentError(BaseError):
    """Raised if Execution is not properly set up with Block."""
    code = ErrorCodeEnv.ENV_ERROR

class EnvironmentBuildError(BaseError):
    """Raised if inputs given to the calculator were incorrect."""
    code = ErrorCodeEnv.ENV_ERROR_BUILD

class EnvironmentUpdateError(BaseError):
    """Raised if inputs given to the calculator were incorrect."""
    code = ErrorCodeEnv.ENV_ERROR_UPDATE




# ==============================================
# Installer related errors
# ==============================================



class ErrorCodeInstall(str,Enum):
    INSTALL_ERROR = 'INSTALL_1001'
    INSTALL_ERROR_INIT = 'INSTALL_1001'
    INSTALL_ERROR_SERIALIZATION = 'INSTALL_1001'
    INSTALL_ERROR_DESERIALIZATION = 'INSTALL_1001'
    INSTALL_ERROR_FILENAME = 'INSTALL_1001'
    INSTALL_ERROR_DEPENDENCY = 'INSTALL_1001'
    INSTALL_ERROR_BUILD = 'INSTALL_1001'
    INSTALL_ERROR_CREATE = 'INSTALL_1001'
    INSTALL_ERROR_REMOVE = 'INSTALL_1001'
    INSTALL_ERROR_METADATA = 'INSTALL_1001'
    INSTALL_ERROR_DIRECTORY = 'INSTALL_1001'
    INSTALL_ERROR_CONFIG = 'INSTALL_1001'
    INSTALL_ERROR_ENVIRON = 'INSTALL_1001'

class InstallError(BaseError):
    """Raised if Install is not properly set up with Block."""
    code = ErrorCodeInstall.INSTALL_ERROR



# ==============================================
# Interface related errors
# ==============================================



class ErrorCodeInterface(str,Enum):
    INTERFACE_ERROR = 'INTERFACE_1001'
    INTERFACE_ERROR_INIT = 'INTERFACE_1001'
    INTERFACE_ERROR_SERIALIZATION = 'INTERFACE_1001'
    INTERFACE_ERROR_DESERIALIZATION = 'INTERFACE_1001'
    INTERFACE_ERROR_BUILD = 'INTERFACE_1001'
    INTERFACE_ERROR_INPUT = 'INTERFACE_1001'
    INTERFACE_ERROR_OUTPUT = 'INTERFACE_1001'
    INTERFACE_ERROR_TRANSFORMER = 'INTERFACE_1001'
    INTERFACE_ERROR_EXECUTE = 'INTERFACE_1001'
    INTERFACE_ERROR_TIMEOUT = 'INTERFACE_1001'

class InterfaceError(BaseError):
    """Raised if Interaface is not properly set up with Block."""
    code = ErrorCodeInterface.INTERFACE_ERROR

class AdvanceInterfaceError(BaseError):
    """Raised if AdvanceInterface is not properly set up with Block."""
    code = ErrorCodeInterface.INTERFACE_ERROR



