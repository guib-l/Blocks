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

from blocks.engine.pyenv import _python_env
from blocks.engine.env import Environment, PYTHON

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
      


    with Environment(functions=heavy_calculation) as ENV:
        print("Do somethings ...")

        print(ENV.backend_env)
        print(ENV.functions)

    print('Out from env')


    temp = copy(PYTHON)
    temp.environment = _python_env
    temp.parameters['packages'] = ['numpy','pandas']

    print('Create new env with packages numpy and pandas')
    print(temp.parameters)

    Environment(name='pip',
                directory='./envs/pip_env',
                language='python3',
                build=False,
                backend_env=temp,
                functions=heavy_calculation)





    sys.exit()
