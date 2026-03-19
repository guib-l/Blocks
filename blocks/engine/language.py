


from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment

from blocks.asset.python3.install import (InstallerPython, 
                                          InstallerPythonWorkflow)

from blocks.interface.communication import LabelCommunication
from blocks.interface.interface import Interface
from blocks.interface.buffer import DataBuffer


class Language:

    @staticmethod
    def _python3_config() -> dict:
        return {
            'installer': InstallerPython,
            'installer_config':{
                'auto':False,
            },
            'environment': EnvironmentBase,
            'environment_config':{
                'name': 'env_001',
                'language': 'python',
                'environment': pyEnvironment,
                'parameters':{
                    'directory': None,
                    'env_name': 'pip-env.01',
                    'env_type': 'venv',
                    'mng_type': 'pip',
                    'dependencies': [],
                    'auto_build': True,
                }
            },
            'executor': Execute,
            'executor_config':{},
            'communicate': LabelCommunication,
            'communicate_config':{},
            'interface': Interface,
            'buffer': DataBuffer
        }

    @classmethod
    def python3_pip(cls, name, directory, dependencies=[], **kwargs):
        config = cls._python3_config()
        config['environment_config']['parameters']['env_name'] = name
        config['environment_config']['parameters']['directory'] = directory
        config['environment_config']['parameters']['dependencies'] = dependencies
        config['environment_config']['parameters'].update(kwargs)
        return config


# ---------------------------------------------------------------------------
# Module-level shortcuts
# Usage: from blocks.engine.language import python3_pip
# ---------------------------------------------------------------------------

def python3_pip(name: str, directory: 'str | None', dependencies: list = [], **kwargs) -> dict:
    """Return a python3/pip language config dict.

    Shortcut for :meth:`Language.python3_pip` usable without instantiation::

        from blocks.engine.language import python3_pip
        proto = Prototype(language=python3_pip(name="my-env", directory="/path"))
    """
    return Language.python3_pip(name=name, directory=directory, dependencies=dependencies, **kwargs)




