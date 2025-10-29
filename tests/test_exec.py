import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *
from blocks.nodes.node import Node

from blocks.socket.interface import (MessageType,MESSAGE,Interface)


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
                    backend='threads',
                    use_shell=None,
                    use_io=False,
                    language=None,
                    signal=None,
                    files=None,)
    print(exe)
    print("Execute instance created successfully.")

    exe_copy = exe.copy()
    print("Execute instance copied successfully.")







    node = Node.load(name='function-test',
                     directory=BLOCK_PATH,
                     _executor=exe,)
    print("Node instance created successfully.")

    print("Testing node execution...")
    #print(node.copy())

    print("===================================")
    print("Starting node execution...")
    node.build()

    result = node.execute(func=heavy_calculation, n=10)
    print(f"Node execution result: {result}")















