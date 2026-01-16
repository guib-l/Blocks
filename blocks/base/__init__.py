import os
import sys

from contextlib import contextmanager


BLOCK_PATH      = "myblock/"
BLOCK_WORKSPACE = None

if 'BLOCK_PATH' in os.environ:
    BLOCK_PATH = os.environ['BLOCK_PATH']

if 'BLOCK_WORKSPACE' in os.environ:
    BLOCK_WORKSPACE = os.environ['BLOCK_WORKSPACE']




@contextmanager
def safe_operation(
        operation_name: str, 
        err_type=None,
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
        raise ERROR(
            err_type=err_type,
            message=f"Unexpected error during {operation_name}",
        ) from e





