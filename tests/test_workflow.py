import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from dataclasses import dataclass
from typing import Any, Dict, TypeVar
from configs import *

from blocks.base import *
from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.socket.interface import (MessageType,MESSAGE,Interface)



@dataclass
class Environment:
    # Placeholder for environment methods 
    # could include setup, teardown, config management, etc.
    __ntype__ = "environment"

@dataclass
class Executor:
    # Placeholder for executor methods 
    # could include task execution, job management, etc.
    __ntype__ = "executor"



if __name__ == "__main__":
      

  
   # Initialisation d'un Block
    node = Node.load(name='function-test',
                     directory=BLOCK_PATH)
    print("Node instance created successfully.")

    # =====================================================
    # Base des tests sur le Workflow

   # Create a sample dataset
    data = {
        'name': 'workflow-1',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        '_mandatory_attr': False,
        'metadata': {'source': 'generated', 'version': 1.0},
        'graphics': {
            'links': None,
            'first': None,
            'last' : None,},
        'type': "workflow",
        '_environment': None,
        '_executor': None,
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

    print("Current Node : \n",workflow.currents_nodes)

    workflow.connect_nodes(1,3)
    workflow.connect_nodes(3,4)

    print(workflow.graphics)



    # =====================================================
    # Execution du workflow

    






