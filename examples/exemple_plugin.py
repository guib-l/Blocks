import os
import time
import copy
from configs import *

from blocks import BLOCK_PATH

from blocks.base import *
from blocks.nodes import *

from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.base.prototype import INSTALLER

#from blocks.engine import PYTHON,PYTHON_PIP,ENVIRONMENT_TYPE
from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment

from os import path
import inspect

from tools.load import PluginLoader, save_function_to_file

def import_modules():

    manager = PluginLoader()

    py_version = f"python{sys.version_info.major}.{sys.version_info.minor}"
    site_packages = os.path.join(
        DIRECTORY, '.envs', 'pip-env.numpy',
        'lib', py_version, 'site-packages'
    )
    script_path = os.path.join(DIRECTORY, 'script', 'script.py')

    manager.load(
        name="script",
        path=script_path,
        site_packages=site_packages,
    )

    # Récupérer le module chargé
    module = manager.get_plugin("script")

    # Lister les fonctions disponibles dans le module
    funcs = [name for name, obj in inspect.getmembers(module, inspect.isfunction)]
    print("Fonctions disponibles :", funcs)

    # Appeler une fonction du module directement
    if hasattr(module, 'basic_function'):
        result = module.basic_function(n=3, delay=0.1)
        print("Résultat :", result)

    return module


def test_environment():

    env = EnvironmentBase(
        name="env_test",
        language="python3",
        environment=pyEnvironment,
        parameters={
            'python_version': '3.8',
            'dependencies': ['numpy', 'pandas'],
        }
    )

    loader = PluginLoader()
    script_path = os.path.join(DIRECTORY, 'script', 'script.py')

    with env as e:
        print("Environnement actif :", e.name)
        print("Version de Python :", e.parameters['python_version'])
        print("Dépendances :", e.parameters['dependencies'])

        
        module = loader.load(
            name=f'script',
            path=script_path,
            site_packages=e.environment.site_packages,
        )
        if hasattr(module, 'basic_function'):
            function = getattr(module, 'basic_function')
            result = module.basic_function(n=2, delay=0.0)
            print(f"[{e.name}] résultat : {result}")
    
    #function(n=5, delay=0.0)  


if __name__ == "__main__":

    #import_modules()

    test_environment()









