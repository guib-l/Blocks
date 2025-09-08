import os,sys
import time
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.base.node import Node


py_script = r"""
import os
import sys

print('Hello World')
"""



if __name__ == "__main__":
    
    BLOCK_DIRECTORY = 'myblock/'
  
   # Create a sample dataset
    data = {
        'name': 'Sample-Dataset',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'values': [1, 2, 3, 4, 5],
        'metadata': {'source': 'generated', 'version': 1.0}
    }
  
   # Initialisation d'un Block
    node = Node(**data)
    print(node)
    print("Node instance created successfully.")
