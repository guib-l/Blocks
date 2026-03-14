import os
import time
from configs import *

from blocks.base import *
from blocks.nodes import *

from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.base.prototype import INSTALLER
from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment



def basic_function(n=5, delay=0.2):
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(delay)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result


def install_node():

    # Create a first basic example of a Node (Prototype) and execute 
    # it in its environment. We have setup all values by default, 
    # so we can just create the Node with its name and type, and 
    # it will be able to find all the necessary information to execute 
    # itself in its environment.

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'.blocks')
    
    # Default environment
    ENVIRONMENT = EnvironmentBase

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
        'environment_config':{
            'name': 'env_001',
            'language': 'python',
            'environment': pyEnvironment,
            'parameters':{
                'directory': os.path.join(BLOCK_PATH, 'envs'),
                'env_name': 'pip-env.01',
                'env_type': 'venv',
                'mng_type': 'pip',
                'dependencies': ['numpy'],
                'auto_build': True,
            }
        },
        'executor': EXECUTE,
        'executor_config':{},
        'methods':[basic_function,],
        'allowed_name':[]
    }

    node = Node(**data)

    # Node installation (if auto is False, it will not create the 
    # Node if it does not exist, but it will check if it exists and 
    # is correctly installed)
    node.install()

    # Node execution
    node.execute(n=4, delay=0.1)

    del node



def load_node():

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'.blocks')
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


def simpliest_node():
    # Node with python3_pip

    from blocks.engine.language import Language

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'.blocks')

    # =============================================

    node = Node(
        name='node_001',
        directory=os.path.join(os.getcwd(),'.blocks'),
        methods=[basic_function,],
        language=Language.python3_pip
    )
    
    node.execute(n=4, delay=0.1)

    # =============================================

    node = Node(
        name='node_001',
        directory=os.path.join(os.getcwd(),'.blocks'),
        methods=[basic_function,],
        language=Language.python3_pip(
            name='pip-env.01',
            directory=os.path.join(BLOCK_PATH, 'envs'),
            dependencies=[]
        )
    )
    
    node.execute(n=4, delay=0.1)


if __name__ == "__main__":

    install_node()

    load_node()

    simpliest_node()





