
from configs import *

from blocks.base.prototype import Prototype

from blocks.base import *

from blocks.base.prototype import INSTALLER
from blocks.engine.environment import Environment


import pytest


class TestPrototypeInitialization:
     """Test Prototype initialization and properties."""
     
     def test_prototype_creation_with_all_parameters(self):
        BLOCK_PATH  = "myprototype/"
        INSTALL     = INSTALLER.PYTHON
        ENVIRONMENT = Environment

        data = {
                'name': 'prototype-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALLER.PYTHON,
                'installer_config':{
                    'auto':True,
                },
                'environment': Environment,
                'environment_config':{},
                'executor': None,
                'executor_config':{},
            }

        prototype = Prototype(**data)
        
        assert prototype.name == 'prototype-test'
        assert prototype.version == '0.0.1'
        #assert prototype.directory == "myprototype/"
        #assert prototype.values == [1, 2, 3, 4, 5]
        #assert prototype.auto_create is True
        #assert prototype.metadata == {'source': 'generated', 'version': 1.0}

