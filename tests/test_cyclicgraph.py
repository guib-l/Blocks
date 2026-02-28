import os,sys
import time
from configs import *

from blocks import BLOCK_PATH

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.nodes.node import Node
from blocks.nodes.graphics import AcyclicGraph
from blocks.nodes.workflow import Workflow

from blocks.engine.execute import Execute

from blocks.engine import INSTALLER

from blocks.engine.environment import Environment

from blocks.interface.buffer import QUEUE
from blocks.interface.communication import COMMUNICATE 
from blocks.interface.interface import INTERFACE

from blocks.utils.logger import logger



if __name__ == "__main__":
    

    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    start = time.time()
    node = Node.load(name='heavy_calculation',
                     ntype='prototype',
                     directory=BLOCK_PATH,
                     ignore_error=True)
    end = time.time()
    print(f'Instance created in {end-start} s.')

    node.execute(n=5)

    workflow = Workflow.load(
        name='workflow-test',
        ntype='workflow',
        directory=BLOCK_PATH,
        ignore_error=True
    )

    workflow.execute(n=5)



    from blocks.nodes.graphics import AcyclicGraph,CyclicGraph

    graph = CyclicGraph()

    graph.add_link(0,1)
    graph.add_link(1,2)

    graph.add_conditional_link(
        origin=2,
        condition_type='IF',
        attr='n',
        case={
            3:{'operator':'==',
               'value':3,},
            4:{'operator':'==',
               'value':4,},
            5:{'operator':'>',
               'value':4,}
        },
        default=3,
    )

    graph.add_link(4,6)

    graph.add_loop_link(
        start=2,
        end=6,
        condition_type='FOR',
        epoch=3
    )

    graph.add_link(6,7)
    graph.add_link(5,7)



