

from configs import *
from blocks.base.dataset import DataSet
from blocks.base.block import Block

from blocks.base import *

import pytest




class TestBlockInitialization:
     """Test Block initialization and properties."""
     
     def test_block_creation_with_all_parameters(self):
          data = {
               'name': 'block-test',
               'id': None,
               'version': '0.0.1',
               'path': "myblock/",
               'values': [1, 2, 3, 4, 5],
               'auto_create': True,
               'metadata': {'source': 'generated', 'version': 1.0}
          }
          block = Block(**data)
          
          assert block.name == 'block-test'
          assert block.version == '0.0.1'
          assert block.path == "myblock/"
          assert block.values == [1, 2, 3, 4, 5]


class TestBlockCopy:
     """Test Block deepcopy functionality."""
     
     def test_block_deepcopy(self):
          data = {'name': 'test-block', 'version': '0.0.1', 'values': [1, 2, 3]}
          block = Block(**data)
          new_block = block.deepcopy()
          assert block == new_block
          assert block is not new_block


class TestBlockVersioning:
     """Test Block version management."""
     
     def test_block_version_update(self):
          block = Block(name='test', version='0.0.1')
          block.version = '0.0.2'
          assert block.version == '0.0.2'
     
     def test_block_version_comparison(self):
          block1 = Block(name='test', version='0.0.1')
          block2 = Block(name='test', version='0.0.1')
          assert block1.version == block2.version






