
import os
import pytest

from blocks.packages import Packages

from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment

BLOCK_PATH = os.path.join(os.getcwd(),'blocks')

class TestPackage:
    
    def test_package_initialization(self):

        data = {
            'directory': os.path.join(BLOCK_PATH, 'envs'),
            'env_name': 'pip-env.01',
            'env_type': 'venv',
            'mng_type': 'pip',
            'dependencies': [],
            'auto_build': True,
        }
        package = Packages(**data)

        assert package.env_name == 'pip-env.01'




