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
    # Placeholder for environment methods 
    # could include setup, teardown, config management, etc.
    ... 

class Executor:
    # Placeholder for executor methods 
    # could include task execution, job management, etc.
    ... 


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
        'ENVIRONMENT': Environment,
        'EXECUTOR': Executor,
    }
  
   # Initialisation d'un Block
    node = Node(**data)
    print(node)
    print("Node instance created successfully.")


    msg = MESSAGE(FROM=node.id, 
                  TO=None, 
                  SUBJECT="test_subject", 
                  DATA={"key": "value"})

    node.input = msg

    print("Input:", node.input)
    print("Info:", node.info())
    print("Output:", node.output)



   # Load new node from the first
    node_bis = Node.load_from_directory(name='Sample-Dataset',
                                        metadata_file='blocks',
                                        path=BLOCK_PATH,
                                        INTERFACE=Interface,
                                        ENVIRONMENT=Environment,
                                        EXECUTOR=Executor)
    print(node_bis)
    print("node instance loaded successfully.")

    node_bis.input = msg

    print("Input:", node_bis.input)
    print("Info:", node_bis.info())
    print("Output:", node_bis.output)


    # Test signal change
    print("Current Signal:", node_bis.sgl())
    node_bis.sgl('RUNNING')
    print("Updated Signal:", node_bis.sgl())
    try:
        node_bis.sgl('INVALID_SIGNAL')
    except Exception as e:
        print("Caught Exception:", e)

    



