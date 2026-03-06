

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

     def test_serialization(self):
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
          serialized = block.to_dict()
          assert isinstance(serialized, dict)
          assert serialized['name'] == 'block-test'
          assert serialized['version'] == '0.0.1'
          assert serialized['path'] == "myblock/"
          assert serialized['values'] == [1, 2, 3, 4, 5]

          block_bis = Block.from_dict(**serialized)
          assert block_bis.name == 'block-test'
          assert block_bis.version == '0.0.1'
          assert block_bis.path == "myblock/"
          assert block_bis.values == [1, 2, 3, 4, 5]

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






