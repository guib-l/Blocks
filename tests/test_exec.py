import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *
from blocks.nodes.node import Node



from blocks.engine.execute import Execute

import time

def heavy_calculation(n=5):
    """Fonction qui sera interruptible."""
    
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
            
    return result



if __name__ == "__main__":
      
    exe = Execute(workdir='./run',
                  commands=None,
                  backend='default',
                  use_shell=False,
                  use_io=False,
                  signal=None,)
    print(exe)
    print("Execute instance created successfully.")

    exe_copy = exe.copy()
    print("Execute instance copied successfully.")


    exec_dict = exe.to_dict()
    Execute.from_dict(**exec_dict)





    node = Node.load(name='HC',
                     ntype='prototype',
                     directory=BLOCK_PATH,
                     executor=exe,)
    import json
    from tools.encoder import EnvJSONEncoder
    print(json.dumps(node.to_dict(), indent=4, cls=EnvJSONEncoder))
    print("Node instance created successfully.")

    print("Testing node execution...")

    print("===================================")
    print("Starting node execution...")

    result = node.execute(n=10)
    print(f"Node execution result: {result}")

















