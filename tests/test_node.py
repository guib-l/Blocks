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
    node = Node.load(name='heavy_calculation',
                     ntype='prototype',
                     directory=BLOCK_PATH)
    end = time.time()
    print(node)
    print("Node instance created successfully.")
    print(f'Instance created in {end-start} s.')

    print(node._register_methods)

    node.execute(n=4)

    print(type(node))
    print(node.registred_files)

    # ===============================================

    _dict = node.to_dict()
    print("Node serialized to dictionary successfully.")
    import json
    from tools.encoder import EnvJSONEncoder
    print(json.dumps(_dict, indent=4, cls=EnvJSONEncoder))


    # Re-create the Node from the dictionary
    node_copy = Node.from_dict(**_dict)
    print("Node deserialized from dictionary successfully.")
    print(node_copy)

    print('Registred methods : ',node_copy._register_methods)

    # TODO: Execute the copied Node
    #print(json.dumps(node_copy.to_dict(), indent=4, cls=EnvJSONEncoder))
    #node_copy.execute(name='heavy_calculation',n=4)




