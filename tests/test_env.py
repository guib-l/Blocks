import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *

from blocks.interface._interface import (MessageType,MESSAGE,Interface)


from blocks.engine.execute import Execute

from blocks.engine.python_env import _empty_env,_python_env
from blocks.engine import PYTHON,PYTHON_PIP
from blocks.engine.environment import Environment

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
      
    # ============================================
    # --- Create new environment with functions ---

    with Environment(functions=heavy_calculation) as ENV:
        print("Do somethings ...")

        print('Backend   : ',ENV.backend)
        print('Functions : ',ENV.functions)

    print('Out from env')

    # ============================================
    # --- Create new environment with packages ---
    print()

    temp = copy(PYTHON_PIP)
    temp.environment = _python_env
    temp.parameters['packages'] = ['numpy','pandas']

    print('Create new env with packages numpy and pandas')

    env = Environment(name='pip',
                      directory='./envs/pip_env/',
                      language='python3',
                      backend_env=temp,
                      functions=heavy_calculation,
                      env_name='generic-env.02'
                )

    print('Build the environment')

    with env as e:
        print("Test of Environment")
        func    = e.get_functions(name='heavy_calculation')
        results = func()

    #env.backend.uninstall()

    
    # ====================================
    # --- Serialization of environment ---
    print()
    
    dict_env = env.to_dict()
    print('Environment as dict : \n',dict_env)
    env = Environment.from_dict(dict_env)

    print(env)

    with env as e:
        print("Test of Environment")
        func    = e.get_functions(name='heavy_calculation')
        results = func(2)
        

    # ====================================
    # --- JSON of the environment ---
    print()
    import json

    dict_results = env.to_dict()

    env = Environment.from_dict(dict_results)

    env.backend.uninstall()

    sys.exit()







