import os
import time
from configs import *

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.nodes.node import Node

from blocks.export import task_node
from blocks.engine.environment import EnvironMixin








if __name__ == "__main__":
      
    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    start = time.time()
    node = Node.load(name='HC',
                     ntype='prototype',
                     directory=BLOCK_PATH)
    end = time.time()
    print(node)
    print("Node instance created successfully.")
    print(f'Instance created in {end-start} s.')

    print(node._register_methods)

    node.execute(n=4)

    print(type(node))


