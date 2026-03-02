import os
import sys

import logging


BLOCK_PATH      = "myblock/"
BLOCK_WORKSPACE = None

if 'BLOCK_PATH' in os.environ:
    BLOCK_PATH = os.environ['BLOCK_PATH']

if 'BLOCK_WORKSPACE' in os.environ:
    BLOCK_WORKSPACE = os.environ['BLOCK_WORKSPACE']



LOG_TO_FILE = False

LOGGER_BLOCK = False
LOGGER_BLOCK_FILE = "blocks.log"
LOGGER_BLOCK_LEVEL = logging.CRITICAL


LOGGER_EXECUTE = False
LOGGER_EXECUTE_FILE = "blocks.log"
LOGGER_EXECUTE_LEVEL = logging.CRITICAL


LOGGER_ENVIRONMENT = False
LOGGER_ENVIRONMENT_FILE = "blocks.log"
LOGGER_ENVIRONMENT_LEVEL = logging.CRITICAL












