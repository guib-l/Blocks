import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *
from blocks.nodes.node import Node
from blocks.export import task_node

from blocks.socket.interface import (MessageType,MESSAGE,Interface)


def export_function(name='function',
                    inp=None,
                    out=None,
                    execute=False,
                    err="defaults-error"):

    def wrap(function):
        def wrapper(**kwargs):
            
            output = {
                'function':function,
                'type':type(function),
                'results':function(**kwargs) if execute else None,
                'input':inp,
                'output':out,
                }

            return output
        return wrapper
    return wrap






@export_function(name='function_test',
                 inp={'xdata':float},
                 out={'ydata':float},
                 err="function-error")
def function_test(xdata):
    print('Execution function_test with xdata =',xdata)
    value = xdata ** 2 + 1.
    return {'ydata':value}



@task_node(backend='default')
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





def add_features(cls):
    """Décorateur qui ajoute des fonctionnalités à une classe."""
    
    class EnhancedClass(cls):
        def __init__(self, node=None, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self.enhanced = True
            self.node = node
        
        def new_feature(self):
            return f"New feature added to {self.__class__.__bases__[0].__name__}"
    
    return EnhancedClass

@add_features   
class Environment:
    # Placeholder for environment methods 
    # could include setup, teardown, config management, etc.
    __ntype__ = "environment"

    def __init__(self):
        pass
    def to_dict(self,):
        return {}


class Executor(Environment):
    # Placeholder for executor methods 
    # could include task execution, job management, etc.
    __ntype__ = "executor"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def to_dict(self,):
        return {}
    



if __name__ == "__main__":
      
   # Create a sample dataset
    data = {
        'name': 'node-test',
        'id': None,
        'version': '0.0.1',
        'path': "myblock/",
        'values': [1, 2, 3, 4, 5],
        '_build': True,
        '_mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        '_environment': None,
        '_executor': None,
    }
  
   # Initialisation d'un Block
    node = Node(**data)
    print(node)
    print("Node instance created successfully.")

    print("Info:", node.info())
    


    # Install few nodes

    script_filename = DIRECTORY + "/myscript/my_script.py" # Ne fonctionne pas
    script_path     = DIRECTORY + "/myscript/source"              # Fonctionne okay

    node = Node.install(name='function-test',
                        directory=os.path.join(DIRECTORY, BLOCK_PATH),
                        files=[script_filename,],
                        _mandatory_attr=False,
                        version='0.0.2',
                        authors=['Block8 Team'],
                        metadata={'description': 'A test function node',
                                  'script': script_filename},
                        _environment=None,
                        _executor=None,)
    print(node)
    print("Node installed successfully.")



    node = Node.load(name='function-test',
                     directory=BLOCK_PATH)
    print(node)
    print("Node instance created successfully.")

    x = function_test(xdata=3.0)
    print("Function output:", x)

    x = heavy_calculation()
    print("Node output:", x)
    
    x.execute(n=5)






