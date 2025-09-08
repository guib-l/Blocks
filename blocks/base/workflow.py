import os
import sys
import io
import uuid
import zipfile
import json
from copy import copy, deepcopy
import csv
from typing import *
from abc import *
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable, Iterator, BinaryIO, TextIO

from .dataset import DataSet
from copy import copy, deepcopy

from blocks.base.baseBlock import BaseBlock
from blocks.base.block import Block

from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from blocks.base.organizer import FileManager, FileError

from blocks.base.encoder import BaseBlockJSONEncoder

T = TypeVar('T', bound='Workflow')



class Workflow(Block):
    def __init__(self,
                 **kwargs):
        
        super().__init__(**kwargs)

    