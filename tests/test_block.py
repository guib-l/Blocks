import os,sys
import time
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *
from blocks.base.dataset import DataSet
from blocks.base.block import Block

from blocks.base import *


py_script = r"""
import os
import sys

print('Hello World')
"""



if __name__ == "__main__":
      
   # Create a sample dataset
    data = {
        'name': 'block-test',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'values': [1, 2, 3, 4, 5],
        'auto_create': True,
        'metadata': {'source': 'generated', 'version': 1.0}
    }
  
   # Initialisation d'un Block
    block = Block(**data)
    print(block)
    print("Block instance created successfully.")
    

    new_block = block.deepcopy()
    print(new_block)
    print("Block copied successfully.")

    if block==new_block:
        print("block et new_block sont égaux")
    else:
        print("block et new_block sont différents")

    # Versionning de block
    print("Current Block Version:", block.version)

    block.version = "0.0.2"
    print("Updated Block Version:", block.version)

    """
   # Compression du block
    block.compress()
    print("Block compressed successfully.")

   # Decompression du block
    block.decompress(source='block-test.zip')
    print("Block decompressed successfully.")

    block.delete_directory("myblock_new")  
    print("Block directory deleted successfully.")
 
   # Save a script file in the block directory
    block.compose("src/script.py", content=py_script)
    print("Script file composed successfully.")

   # Compression du block
    block.compress()
    print("Block compressed successfully.")

   # Decompression du block
    block.decompress(source='block-test.zip')
    print("Block decompressed successfully.")

   # Rename the block
    block.rename("New-block-test")
    print("Block renamed successfully.")

   # Rename the block
    block.rename("block-test")
    print("Block renamed successfully.")
    
   # Move the block
    block.move("myblock_new/")
    print("Block moved successfully.")

    block.delete_directory("myblock_new")  
    print("Block directory deleted successfully.")
    """

    new_block = block.deepcopy()
    print(new_block)
    print("Block copied successfully.")

    if block==new_block:
        print("block et new_block sont égaux")
    else:
        print("block et new_block sont différents")

    # Versionning de block
    print("Current Block Version:", block.version)

    block.version = "0.0.2"
    print("Updated Block Version:", block.version)

    
