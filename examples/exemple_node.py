import os
import time
from configs import *

from blocks import BLOCK_PATH

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.base.prototype import INSTALLER

from blocks.export import task_node
from blocks.engine.environment import Environment


def basic_function(n=5, delay=0.2):
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(delay)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result







