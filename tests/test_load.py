import os
import sys
import time

from configs import *
from blocks.base import *

from tools.load import (
    _import_modules,_load_function_from_file,
    _load_callable_from_file,_load_function_with_dependencies,
    _load_function_without_decorators
)

from blocks.export import task_node
from blocks.base.prototype import Prototype

import inspect


def wait(to=0.02):
    time.sleep(0.01)
    return 

def heavy_calculation(n=5):
    """Fonction qui sera interruptible."""
    
    result = 0
    for i in range(n):
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
            
    return result

def low_calculation(n=5):
    """Fonction qui sera interruptible."""
    
    result = 0
    for i in range(n):
        result += i
        wait(to=0.01)
        print(f"Calcul en cours... étape {i+1}/{n}")
            
    return result


#@task_node(backend    = 'default',
#           directory  = BLOCK_PATH,
#           execute    = None,
#           objectType = Prototype,)

def task(func):
    """Decorator to mark a function as a task node."""
    def wrapper(*args, **kwargs):
        print('decorator')
        return func(*args, **kwargs)
    return wrapper

@task
def medium_calculation(n=5):
    """Fonction qui sera interruptible."""
    result = 0
    for i in range(n):
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result




if __name__ == "__main__":

    filepath = 'test_load.py'
    mods = _import_modules(filepath)
    print(mods)

    func = _load_function_from_file(filepath, 'heavy_calculation')
    print(func)

    func = _load_callable_from_file(filepath, 'low_calculation')
    print(func)
    func(5)

    func = _load_function_with_dependencies(filepath, 'low_calculation')
    print(func)

    func = _load_function_without_decorators(filepath, 'medium_calculation')
    print(func)
    func(5)

    print( [obj for name, obj in inspect.getmembers(mods) 
                     if inspect.isfunction(obj)] )






