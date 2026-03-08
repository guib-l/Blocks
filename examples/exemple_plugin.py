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

from blocks.engine import PYTHON,PYTHON_PIP,ENVIRONMENT_TYPE
from blocks.engine.execute import Execute
from blocks.engine.environment import Environment
from blocks.engine.python3.envPy import EnvPython

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
    result = module.basic_function(n=3, delay=0.1)
    print("Résultat :", result)

    # Accéder à un attribut ou une variable du module
    # print(module.MY_CONSTANT)

    return module


if __name__ == "__main__":

    import_modules()











