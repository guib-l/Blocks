import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *
from blocks.nodes.node import Node
from blocks.export import task_node,export_function

from blocks.interface._interface import (MessageType,MESSAGE,Interface)


install_directory = os.path.join(DIRECTORY, BLOCK_PATH)




@export_function(name='function_test',
                 inp={'xdata':float},
                 out={'ydata':float},
                 err="function-error")
def function_test(xdata):
    print('Execution function_test with xdata =',xdata)
    value = xdata ** 2 + 1.
    return {'ydata':value}


@task_node()
def print_data(args):
    print(f'> Argument {args}')



@task_node(install=True,
           directory=install_directory)
def heavy_calculation(n=5):
    """Fonction qui sera interruptible."""
    import time
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result





if __name__ == "__main__":
      
   # Create a sample dataset
    data = {
        'name': 'node-test',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'values': [1, 2, 3, 4, 5],
        'auto': True,
        'install': True,
        'mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'environment': None,
        'executor': None,
    }
  
    # ===============================================
    # Initialisation d'un Block
    print("\n"+"*"*40)
    print("BUILD NODE with default_install")
    node = Node(**data)
    print("Node instance created successfully.") 


    # ===============================================
    # Install few nodes
    print("\n"+"*"*40)
    print("INSTALL NODE with default_install")
    print(f' > Directory : {DIRECTORY}')

    script_filename = DIRECTORY + "/myscript/my_script.py" # Ne fonctionne pas
    script_path     = DIRECTORY + "/myscript/source"       # Fonctionne okay

    node = Node.install(name='function-test',
                        directory=os.path.join(DIRECTORY, BLOCK_PATH),
                        files=[script_filename,],
                        mandatory_attr=False,
                        version='0.0.2',
                        authors=['Blocks Team'],
                        metadata={'description': 'A test function node',
                                  'script': script_filename},
                        environment=None,
                        executor=None,)
    print(node)
    print("Node installed successfully.")



    # ===============================================
    print("\n"+"*"*40)
    print("LOAD NODE with loading method")

    node = Node.load(name='function-test',
                     directory=BLOCK_PATH)
    print(node)
    print("Node instance created successfully.")



    # ===============================================
    print("\n"+"*"*40)
    print("TASK NODE with loading method")

    x = function_test(xdata=3.0)
    print("Function output:", x)

    from tools.load import _load_function_from_file

    func = _load_function_from_file(
        '/home/workstation/Documents/Blocks/tests/myscript/my_script.py', 
        'say')

    print(func)
    func('helle')




    sys.exit()
    # ===============================================
    print("\n"+"*"*40)
    print("LOAD/BUILD NODE with task_node TRANSFORMATION")

    results = heavy_calculation(n=2)  

    
    node = heavy_calculation() 
    print('> Type of object : ',node.__class__)

    node.execute(n=5)

    print(node.executor)
    print(node.environment)

    # Installation de via Task (DONE)
    node = Node.load('task_heavy_calculation',
                      directory=BLOCK_PATH)
    node.execute(n=3)

    # Env default python pip + conda + venv







