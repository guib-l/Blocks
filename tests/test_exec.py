import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from blocks.base import *
from blocks.nodes.node import Node



from blocks.engine.execute import Execute

import time
import json



if __name__ == "__main__":
      
    exe = Execute(workdir='./run',
                  commands=None,
                  backend='threads',
                  use_shell=False,
                  use_io=False,
                  build_backend=True,
                  signal=None,)
    print(exe)
    print("Execute instance created successfully.")

    #exe_copy = exe.copy()
    #print("Execute instance copied successfully.")


    exec_dict = exe.to_dict()

    print(json.dumps(exec_dict,indent=4))

    fr_exec = Execute.from_dict(**exec_dict)
    print(fr_exec)
    print("Execute instance serialized and deserialized successfully.")

    node = Node.load(name='HC',
                     ntype='prototype',
                     directory=BLOCK_PATH,
                     executor=Execute,
                     stdout='LOGGER', )
    
    from tools.encoder import EnvJSONEncoder
    print(json.dumps(node.to_dict(), indent=4, cls=EnvJSONEncoder))
    print("Node instance created successfully.")

    print("Testing node execution...")

    print("===================================")
    print("Starting node execution...")

    result = node.execute(n=4)
    print(f"Node execution result: {result}")

















