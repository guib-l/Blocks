import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.base import *
from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

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
      

  
   # Initialisation d'un Block
    node = Node.load(name='Sample-Dataset',
                     directory=BLOCK_PATH)
    print("Node instance created successfully.")



   # Create a sample dataset
    data = {
        'name': 'workflow-1',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'metadata': {'source': 'generated', 'version': 1.0},
        'graphics': {
            'links': None,
            'first': None,
            'last' : None,},
        'type': "workflow",
        '_interface': Interface,
        '_environment': Environment,
        '_executor': Executor,
    }

   # Create a sample workflow
    workflow = Workflow(**data)
    print(workflow)
    print("Workflow instance created successfully.")

    print(workflow.graphics)
    print("Graphics of workflow initialized")

    workflow.add_node(node,1)
    workflow.add_node(node,3)
    workflow.add_node(node,)
    workflow.add_node(node,)

    print(workflow.currents_nodes)

    workflow.connect_nodes(1,3)
    workflow.connect_nodes(3,4)

    print(workflow.graphics)










