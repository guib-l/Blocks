import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.interface.interface import (Interface)


from blocks.engine.execute import Execute

from blocks.engine.envPy import EnvEmpty,EnvPython
from blocks.engine import PYTHON,PYTHON_PIP,ENVIRONMENT_TYPE
from blocks.engine.environment import EnvironMixin, Environment

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


   # Create a sample dataset
    data = {
        'name': 'prototype-test',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'mandatory_attr': False,
        'methods': [heavy_calculation,],
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'environment': EnvironMixin,
        'executor': None,
    }
  
    # ===============================================
    # Initialisation d'un Prototype
    print("\n"+"*"*40)

    print("BUILD PROTOTYPE in-place")
    
    proto = Prototype(auto_create=False,
                      **data)
    print(proto)
    print("Prototype instance created successfully.") 

    # ============================================
    # --- Create new environment with functions ---
    print("\n"+"*"*40)

    with proto as proto.environ:
        print("Test of Prototype environment")
        func    = proto.environ.get_methods(name='heavy_calculation')
        results = func(2)
        print("Results :",results)

    status = proto.__diff__(ENVIRONMENT_TYPE.PYTHON_PIP)

    print('Equivalence : ',status)




    # ============================================
    # --- Create new Environment with packages ---
    print("\n"+"*"*40)


    temp = copy(PYTHON_PIP)
    temp.environment = EnvPython
    temp.parameters['packages'] = ['numpy','pandas']

    print('Create new env with packages numpy and pandas')


    env = Environment(name='pip',
                      directory='./envs/pip_env/',
                      language='python3',
                      backend_env=temp,
                      env_name='generic-env.02'
                )

    print('Build the environment')

    with env as e:
        print("Test of Environment")

    #sys.exit()


    
    # ====================================
    # --- Serialization of environment ---
    print("\n"+"*"*40)
    
    dict_env = env.to_dict()
    print('Environment as dict : \n',dict_env)

    env_from_dict = Environment.from_dict(**dict_env)

    print(env_from_dict)

    with env_from_dict as e:
        print("Test of Environment")
        

    # ====================================
    # --- JSON of the environment ---
    print("\n"+"*"*40)

    dict_results = env.to_dict()

    env = Environment.from_dict(**dict_results)
    env.backend.uninstall()

    sys.exit()







