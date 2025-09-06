import os,sys
import time
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *
from blocks.base.dataset import DataSet
from blocks.base.block import Block


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
    block = Block(**data)
    print(block)
    print("Block instance created successfully.")
    
    # Write metadata (block.json)
    Block.export_metadata(block, filename='blocks', format='json')
  
   # Load new Block from the first
    block_bis = Block.load_from_directory(name='Sample-Dataset',
                                          metadata_file='blocks',
                                          path=BLOCK_DIRECTORY)
    print(block_bis)
    print("Block instance loaded successfully.")
  
   # Save a script file in the block directory
    block.compose("src/script.py", content=py_script)
    print("Script file composed successfully.")

   # Compression du block
    block.compress()
    print("Block compressed successfully.")

   # Decompression du block
    block.decompress(source='Sample-Dataset.zip')
    print("Block decompressed successfully.")

   # Rename the block
    block.rename("New-Sample-Dataset")
    print("Block renamed successfully.")

   # Rename the block
    block.rename("Sample-Dataset")
    print("Block renamed successfully.")

   # Move the block
    block.move("myblock_new/")
    print("Block moved successfully.")

    block.delete_directory("myblock_new")  
    print("Block directory deleted successfully.")





