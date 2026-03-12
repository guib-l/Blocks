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
from blocks.asset.python3.envPy import EnvPython



def install_node():

    # Create a first basic example of a Node (Prototype) and execute 
    # it in its environment. We have setup all values by default, 
    # so we can just create the Node with its name and type, and 
    # it will be able to find all the necessary information to execute 
    # itself in its environment.

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'blocks')
    
    # Default environment
    ENVIRONMENT = Environment

    ENVIRONMENT_CONFIG = {
        'environment':EnvPython,
        'language':'python3',
        'parameters':{
            'directory': './envs/pip_env/',
            'env_name': 'generic-env.01',
            'env': 'venv',
            'mng': 'pip',
            'dependencies': ['numpy'],
            'auto_build': True,
            'profile': None,}
    }

    temp = copy.copy(PYTHON_PIP)
    temp.environment = EnvPython
    temp.parameters['packages'] = ['numpy',]

    ENVIRONMENT_CONFIG = {
        'name':'pip',
        'directory':'./envs/pip_env/',
        'language':'python3',
        'backend_env':temp,
        'env_name':'generic-env.01',
    } 

    # Default installer for python programmes
    INSTALL = INSTALLER.PYTHON

    # Default mothod to execute the Node
    EXECUTE = Execute

    data = {
        'name': 'node_001',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'description': 'A simple Node for testing'},
        'installer': INSTALL,
        'installer_config':{
            'auto':False, # Create the Node if it does not exist
        },
        'environment': ENVIRONMENT,
        'environment_config':ENVIRONMENT_CONFIG,
        'executor': EXECUTE,
        'executor_config':{},
        'files':["script/script.py"],
        'methods':[],
        'allowed_name':['basic_function']
    }

    node = Node(**data)

    # Node installation (if auto is False, it will not create the 
    # Node if it does not exist, but it will check if it exists and 
    # is correctly installed)
    #node.install()

    # Node execution
    node.execute(n=4, delay=0.1)

    #del node



def load_node():

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'blocks')
    # ===============================================
    # Load the Node from its directory and execute it in its environment.
    import time

    start = time.time()
    node = Node.load(name='node_001',
                     ntype='node',
                     directory=BLOCK_PATH)
    print(node)
    print("Node instance created successfully.")
    end = time.time()

    print(f'Instance created in {end-start} s.')

    start = time.time()
    node.execute(n=2, delay=0.3)
    end = time.time()
    print(f'Dead-Time of Node execution in {end-start-2*0.3} s.')





if __name__ == "__main__":

    install_node()

    #load_node()






