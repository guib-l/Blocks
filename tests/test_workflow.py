import os,sys
import time
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.base.workflow import Workflow


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
    workflow = Workflow(**data)
    print(workflow)
    print("workflow instance created successfully.")




