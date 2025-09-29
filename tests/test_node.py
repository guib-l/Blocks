import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.base.node import Node
from blocks.base import *

from blocks.socket.interface import (MessageType,MESSAGE,Interface)


py_script = r"""
import os
import sys

print('Hello World x2')
"""

class Environment:
    ... # Placeholder for environment methods 
    # could include setup, teardown, config management, etc.



if __name__ == "__main__":
      
   # Create a sample dataset
    data = {
        'name': 'Sample-Dataset',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'values': [1, 2, 3, 4, 5],
        'metadata': {'source': 'generated', 'version': 1.0},
        'INTERFACE': Interface,
        'ENVIRONMENT': Environment
    }
  
   # Initialisation d'un Block
    node = Node(**data)
    print(node)
    print("Node instance created successfully.")


    msg = MESSAGE(FROM=node.id, 
                  TO=None, 
                  SUBJECT="test_subject", 
                  DATA={"key": "value"})

    node.__ITFC__.input = msg

    print(node.input)



   # Load new node from the first
    node_bis = Node.load_from_directory(name='Sample-Dataset',
                                        metadata_file='blocks',
                                        path=BLOCK_PATH,
                                        INTERFACE=Interface,
                                        ENVIRONMENT=Environment)
    print(node_bis)
    print("node instance loaded successfully.")












