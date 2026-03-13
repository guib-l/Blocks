
import os
import time
import sys

from configs import *

from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironmentBase
from blocks.asset.python3.env import pyEnvironment


from blocks.asset.python3.install import (InstallerPython, 
                                          InstallerPythonWorkflow)

from blocks.engine.oriented import AcyclicGraphic
from blocks.interface.communication import COMMUNICATE
from blocks.interface.interface import INTERFACE
from blocks.interface.buffer import BUFFER


from blocks.engine.transformer import Transformer


def install_workflow():
    
    # Create a first basic example of a Workflow and execute 
    # it in its environment. We have setup all values by default, 
    # so we can just create the Workflow with its name and type, and 
    # it will be able to find all the necessary information to execute 
    # itself in its environment.

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'blocks')

    node = Node.load(name='node_002',
                     ntype='node',
                     directory=BLOCK_PATH)

    print(node)
    print("Node instance created successfully.")
    #sys.exit()
    
    # Default environment
    ENVIRONMENT = EnvironmentBase

    TRANSFORMER = Transformer(
        rename_attr=[('result', 'n'),]
    )
    # Default installer for python programmes
    INSTALL = InstallerPythonWorkflow

    # Default mothod to execute the Node
    EXECUTE = Execute

    data = {
        'name': 'workflow_001',
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
        'graphics': AcyclicGraphic,
        'graphics_config':{
            'links':[('HC_node_1', 'HC_node_2'),],
            'first':'HC_node_1',
            'last':None,
        },
        'communicate': COMMUNICATE.LABEL,
        'communicate_config':{},
        'interface': INTERFACE.SIMPLE,
        'buffer': BUFFER.DATABUFFER,  
        'register_nodes':{
            'HC_node_1': {'node':'node_001', 
                          'directory':BLOCK_PATH,
                          'method_name':'basic_function',
                          'ntype':Node,
                          'transformer': None},
            'HC_node_2': {'node':node,
                          'method_name':'basic_function',
                          'ntype':Node,
                          'transformer': TRANSFORMER},
        }
    }

    workflow = Workflow(**data)

    # Node installation (if auto is False, it will not create the 
    # Node if it does not exist, but it will check if it exists and 
    # is correctly installed)
    workflow.install()

    # Node execution
    workflow.execute(n=4, delay=0.1)

    del workflow



def load_workflow():
    
    # Create a first basic example of a Workflow and execute 
    # it in its environment. We have setup all values by default, 
    # so we can just create the Workflow with its name and type, and 
    # it will be able to find all the necessary information to execute 
    # itself in its environment.

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'blocks')

    workflow = Workflow.load(name='workflow_001',
                             ntype='workflow',
                             directory=BLOCK_PATH)

    print(workflow)
    print("Workflow instance created successfully.")
    
    workflow.execute(n=4, delay=0.1)


def mix_node_and_workflow():

    # Create a first basic example of a Workflow and execute 
    # it in its environment. We have setup all values by default, 
    # so we can just create the Workflow with its name and type, and 
    # it will be able to find all the necessary information to execute 
    # itself in its environment.

    # Directory where the Node is located
    BLOCK_PATH = os.path.join(os.getcwd(),'blocks')

    node = Node.load(name='node_002',
                     ntype='node',
                     directory=BLOCK_PATH)
    
    print("Node instance created successfully.")

    workflow = Workflow.load(name='workflow_001',
                             ntype='workflow',
                             directory=BLOCK_PATH)

    print(workflow)
    print("Workflow instance created successfully.")

    TRANSFORMER = Transformer(
        additional_parameters={'delay':0.001},
        rename_attr=[('result', 'n'),]
    )

    with workflow as wf:
        wf.import_node(label='HC_node_3', 
                       node=node, 
                       transformer=TRANSFORMER)
        wf.add_link('HC_node_2', 'HC_node_3')
        
    wf.execute(n=4, delay=0.1)






if __name__ == "__main__":

    install_workflow()

    load_workflow()

    mix_node_and_workflow()

