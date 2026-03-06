
from configs import *


import pytest


class TestNodeInitialization:
    """Test Node initialization and properties."""
     
    def test_node(self):

        from blocks.nodes.node import Node

        from blocks.base.prototype import INSTALLER
        from blocks.engine.installer import Installer
        from blocks.engine.execute import Execute
        from blocks.engine.environment import Environment

        BLOCK_PATH  = "mynode/"
        INSTALL     = Installer
        EXECUTE     = Execute
        ENVIRONMENT = Environment

        data = {
                'name': 'node-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALL,
                'installer_config':{
                    'auto':False,
                },
                'environment': ENVIRONMENT,
                'environment_config':{},
                'executor': EXECUTE,
                'executor_config':{},
            }
        
        node = Node(**data)
        assert node.name == 'node-test'
        assert node.version == '0.0.1'
        assert node.directory == "mynode/"

        assert isinstance(node.environment, Environment)
        assert isinstance(node.installer, Installer)
        assert isinstance(node.executor, Execute)








