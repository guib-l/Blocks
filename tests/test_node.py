import os,sys
import time
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.base.node import Node


py_script = r"""
import os
import sys

print('Hello World x2')
"""

class Protocole:
    def send(self, message: str) -> None:
        print(f"Sending message: {message}")

    def receive(self) -> str:
        return "Received message"
    


if __name__ == "__main__":
    
    BLOCK_DIRECTORY = 'myblock/'
  
   # Create a sample dataset
    data = {
        'name': 'Sample-Dataset',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'values': [1, 2, 3, 4, 5],
        'metadata': {'source': 'generated', 'version': 1.0},
        'PROTOCOLE': Protocole
    }
  
   # Initialisation d'un Block
    node = Node(**data)
    print(node)
    print("Node instance created successfully.")



   # Load new node from the first
    node_bis = Node.load_from_directory(name='Sample-Dataset',
                                        metadata_file='blocks',
                                        path=BLOCK_DIRECTORY,
                                        PROTOCOLE=Protocole)
    print(node_bis)
    print("node instance loaded successfully.")



    Node.install()

    Node.uninstall()


    

    Node.load()







