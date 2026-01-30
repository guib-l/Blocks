import os
import sys



BLOCK_PATH      = "myblock/"
BLOCK_WORKSPACE = None

if 'BLOCK_PATH' in os.environ:
    BLOCK_PATH = os.environ['BLOCK_PATH']

if 'BLOCK_WORKSPACE' in os.environ:
    BLOCK_WORKSPACE = os.environ['BLOCK_WORKSPACE']





LOGGER_BLOCK = True
LOGGER_BLOCK_FILE = ""

LOGGER_EXECUTE = True
LOGGER_EXECUTE_FILE = ""

LOGGER_ENVIRONMENT = True
LOGGER_ENVIRONMENT_FILE = ""













