
from configs import *


import pytest

from blocks.nodes.node import Node
from blocks.base.prototype import INSTALLER
from blocks.engine.installer import Installer
from blocks.asset.python3.install import InstallerPython
from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment


class TestNodeInitialization:
    """Test Node initialization and properties."""
     
    def test_node(self):
     
        BLOCK_PATH  = "mynode/"
        INSTALL     = Installer
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase

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
                'environment_config':{
                    'name': 'env_001',
                    'language': 'python',
                    'environment': pyEnvironment,
                    'parameters':{
                        'directory': os.path.join(BLOCK_PATH, 'envs'),
                        'env_name': 'pip-env.01',
                        'env_type': 'venv',
                        'mng_type': 'pip',
                        'dependencies': [],
                        'auto_build': True,
                    }
                },
                'executor': EXECUTE,
                'executor_config':{},
            }
        
        node = Node(**data)
        assert node.name == 'node-test'
        assert node.version == '0.0.1'
        assert node.directory == "mynode/"   # type: ignore[attr-defined]

        assert isinstance(node.environment, EnvironmentBase)
        assert isinstance(node.installer, Installer)
        assert isinstance(node.executor, Execute)








