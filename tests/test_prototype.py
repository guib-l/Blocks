
from configs import *


import pytest

from blocks.base.prototype import Prototype

from blocks.base.prototype import INSTALLER
from blocks.engine.installer import Installer
from blocks.asset.python3.install import InstallerPython
from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment

BLOCK_PATH  = "myblock/"

def basic_function(n):
    return n*2

class TestPrototypeInitialization:
    """Test Prototype initialization and properties."""
     
    def test_prototype(self):

        INSTALL     = Installer
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase

        data = {
                'name': 'prototype-test',
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

        prototype = Prototype(**data)
        
        assert prototype.name == 'prototype-test'
        assert prototype.version == '0.0.1'
        assert prototype.directory == BLOCK_PATH  # type: ignore[attr-defined]

        assert isinstance(prototype.environment, EnvironmentBase)
        assert isinstance(prototype.installer, Installer)
        assert isinstance(prototype.executor, Execute)


    def test_prototype_serialization(self):
        
        INSTALL     = Installer
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase

        data = {
                'name': 'prototype-test',
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

        prototype = Prototype(**data)
        serialized = prototype.to_dict()

        assert isinstance(serialized, dict)
        assert serialized['name'] == 'prototype-test'
        assert serialized['version'] == '0.0.1'
        assert serialized['directory'] == BLOCK_PATH

        prototype_bis = Prototype.from_dict(**serialized)
        
        assert prototype_bis.name == 'prototype-test'
        assert prototype_bis.version == '0.0.1'
        assert prototype_bis.directory == BLOCK_PATH  # type: ignore[attr-defined]

    def test_prototype_install_z(self):
        """Test the installation process of a prototype."""

        INSTALL     = InstallerPython
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase

        data = {
                'name': 'prototype-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALL,
                'installer_config':{
                    'auto':True,
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

        prototype = Prototype(**data)
        
        # Test installation (this will depend on the actual implementation of the installer)
        try:
            prototype.install()
            installed = True
        except Exception as e:
            print(f"Installation failed: {e}")
            installed = False
        
        assert installed, "Prototype installation should succeed."

    def test_prototype_install_with_method(self):

        """Test the installation process of a prototype with a method."""
        from blocks.base.prototype import Prototype

        INSTALL     = InstallerPython
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase


        data = {
                'name': 'prototype-method-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALL,
                'installer_config':{
                    'auto':True,
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
                'methods':[basic_function],
            }

        prototype = Prototype(**data)
        
        # Test installation (this will depend on the actual implementation of the installer)
        try:
            prototype.install()
            installed = True
        except Exception as e:
            print(f"Installation failed: {e}")
            installed = False
        
        assert installed, "Prototype installation should succeed."

    def test_prototype_install_files(self):
        """Test the installation process of a prototype with files."""
        from blocks.base.prototype import Prototype

        INSTALL     = InstallerPython
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase


        data = {
                'name': 'prototype-file-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALL,
                'installer_config':{
                    'auto':True,
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
                'files':['myscript/my_script.py',],
            }

        prototype = Prototype(**data)
        
        # Test installation (this will depend on the actual implementation of the installer)
        try:
            prototype.install()
            installed = True
        except Exception as e:
            print(f"Installation failed: {e}")
            installed = False
        
        assert installed, "Prototype installation should succeed."

    def test_prototype_install_with_method_and_files(self):

        """Test the installation process of a prototype with both methods and files."""

        INSTALL     = InstallerPython
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase


        data = {
                'name': 'prototype-method-file-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALL,
                'installer_config':{
                    'auto':True,
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
                'methods':[basic_function],
                'files':['myscript/my_script.py',],
            }

        prototype = Prototype(**data)
        
        # Test installation (this will depend on the actual implementation of the installer)
        try:
            prototype.install()
            installed = True
        except Exception as e:
            print(f"Installation failed: {e}")
            installed = False
        
        assert installed, "Prototype installation should succeed."

    def test_prototype_install_with_allowed_names(self):

        """Test the installation process of a prototype with allowed names."""

        INSTALL     = InstallerPython
        EXECUTE     = Execute
        ENVIRONMENT = EnvironmentBase


        data = {
                'name': 'prototype-allowed-names-test',
                'id': None,
                'version': '0.0.1',
                'directory':BLOCK_PATH,
                'mandatory_attr': False,
                'metadata': {'source': 'generated', 
                             'version': 1.0,
                             'description': 'A sample dataset for testing'},
                'installer': INSTALL,
                'installer_config':{
                    'auto':True,
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
                'methods':[basic_function],
                'files':['myscript/my_script.py',],
                'allowed_name':['basic_function',],
            }

        prototype = Prototype(**data)
        
        # Test installation (this will depend on the actual implementation of the installer)
        try:
            prototype.install()
            installed = True
        except Exception as e:
            print(f"Installation failed: {e}")
            installed = False
        
        assert installed, "Prototype installation should succeed."


    def test_prototype_load(self):
        """Test loading a prototype from disk."""

        try:
            loaded_prototype = Prototype.load(
                name='prototype-method-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."

    def test_prototype_execute(self):
        """Test executing a method of the prototype."""
        from blocks.base.prototype import Prototype

        loaded_prototype = None
        result = None
        try:
            loaded_prototype = Prototype.load(
                name='prototype-method-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."

        try:
            result = loaded_prototype.execute(name='basic_function', n=5)  # type: ignore[union-attr]
            executed = True
        except Exception as e:
            print(f"Execution failed: {e}")
            executed = False
        
        assert executed, "Prototype method execution should succeed."
        assert result == 10, "The result of basic_function(5) should be 10."

    def test_prototype_uninstall(self):
        """Test uninstalling the prototype."""
        from blocks.base.prototype import Prototype

        loaded_prototype = None
        try:
            loaded_prototype = Prototype.load(
                name='prototype-allowed-names-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."
        
        try:
            loaded_prototype.uninstall()  # type: ignore[union-attr]
            uninstalled = True
        except Exception as e:
            print(f"Uninstallation failed: {e}")
            uninstalled = False
        
        assert uninstalled, "Prototype uninstallation should succeed."

    def test_prototype_basic_use(self):
        """Test the basic use case of creating, installing, loading, and executing a prototype."""
        from blocks.base.prototype import Prototype

        proto = None
        try:
            proto = Prototype.load(
                name='prototype-file-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."

        try:
            proto.installer.move(os.path.join('..', 'myscript'),   # type: ignore[union-attr]
                                 erase_source=True )
            proto.installer.move(BLOCK_PATH,   # type: ignore[union-attr]
                                 erase_source=True )
            moved = True
        except:
            print("Moving files failed.")
            moved = False

        assert moved, "Moving prototype files should succeed."

        try:
            proto.installer.rename("basics_prototype")  # type: ignore[union-attr]
            renamed = True
        except:
            print("Renaming prototype failed.")
            renamed = False

        assert renamed, "Renaming prototype should succeed."

    def test_prototype_compress(self):
        """Test compressing and decompressing the prototype."""
        from blocks.base.prototype import Prototype

        proto = None
        try:
            proto = Prototype.load(
                name='prototype-file-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."

        try:
            proto.installer.compress()  # type: ignore[union-attr]
            compressed = True
        except Exception as e:
            print(f"Compression failed: {e}")
            compressed = False
        
        assert compressed, "Prototype compression should succeed."

        try:
            proto.installer.decompress()  # type: ignore[union-attr]
            decompressed = True
        except Exception as e:
            print(f"Decompression failed: {e}")
            decompressed = False
        
        assert decompressed, "Prototype decompression should succeed."












