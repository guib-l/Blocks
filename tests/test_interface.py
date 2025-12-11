import os
import sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.nodes.node import Node
from blocks.base import *

from blocks.interface.interface import Interface


if __name__ == "__main__":

    # ===============================================
    # Initialisation d'un Noeud
    print("\n"+"*"*40)

    node = Node.load('task_heavy_calculation',
                      directory=BLOCK_PATH)
    node.execute(n=5)


    sys.exit()
