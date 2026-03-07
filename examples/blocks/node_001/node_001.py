from blocks import BLOCK_PATH
from blocks.base import *
from blocks.base.prototype import INSTALLER
from blocks.engine.environment import Environment
from blocks.engine.execute import Execute
from blocks.nodes import *
from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow
from configs import *
import os
import time


def basic_function(n=5, delay=0.2):
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(delay)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result


