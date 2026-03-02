import os
import sys
import json

from blocks import *

from typing import *
from abc import *
from pathlib import Path
from enum import Enum

import logging


# TODO: Pouvoir choisir si la sortie doit être redirigée 
# vers la console ou un fichier
# TODO: Faire un véritable setter de logs (propre)


def colorize(text,color_code,style_code=None):
    style = f"\033[{style_code};" if style_code else "\033["
    return f"{style}{color_code}m{text}\033[0m"


LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)



class ColoredFormatter(logging.Formatter):
    COLORS = {
        'DEBUG': '\033[36m',    # Cyan
        'INFO': '\033[32m',     # Green
        'WARNING': '\033[33m',  # Yellow
        'ERROR': '\033[31m',    # Red
        'CRITICAL': '\033[35m', # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, '')
        record.levelname = f"{log_color}{record.levelname:>8}{self.RESET}"
        return super().format(record)



class StreamLogger:
    def __init__(self, logger, level=logging.DEBUG):
        self.logger = logger
        self.level = level

    def write(self, message):
        if message.strip():
            self.logger.log(self.level, message.strip())

    def flush(self):
        pass

   

def setup_logger(
        name='BLOCKS',
        level=logging.DEBUG,
        log_filename='blocks.log',
        log_format=None,
        log_directory='.',
        log_to_file=False ):
    
    if log_to_file:

        if not os.path.exists(log_directory):
            os.makedirs(log_directory)

    logger = logging.getLogger(name)
    logger.setLevel(level)

    if log_format is None:
        log_format = ColoredFormatter(
            "%(levelname)s - %(asctime)s - %(name)s - %(message)s",
                datefmt='%Y-%m-%d %H:%M:%S'
        )

    # Handler pour la console
    c_handler = logging.StreamHandler()
    c_handler.setLevel(level)
    c_handler.setFormatter(log_format)

    logger.addHandler(c_handler)

    if log_to_file:

        # Handler pour un fichier
        f_handler = logging.FileHandler(
            os.path.join(log_directory,log_filename))
        f_handler.setLevel(level)
        f_handler.setFormatter(log_format)

        logger.addHandler(f_handler)
    
    return logger





logger = setup_logger(
        name='BLOCKS ',
        level=LOGGER_BLOCK_LEVEL,
        log_filename=LOGGER_BLOCK_FILE,
        log_format=None,
        log_directory='.',
        log_to_file=LOG_TO_FILE    
)
    
    
exec_logger = setup_logger(
        name='EXECUTE',
        level=LOGGER_EXECUTE_LEVEL,
        log_filename=LOGGER_EXECUTE_FILE,
        log_format=None,
        log_directory='.',
        log_to_file=LOG_TO_FILE    
)

env_logger = setup_logger(
        name='ENVIRON',
        level=LOGGER_ENVIRONMENT_LEVEL,
        log_filename=LOGGER_ENVIRONMENT_FILE,
        log_format=None,
        log_directory='.',
        log_to_file=LOG_TO_FILE    
)


















