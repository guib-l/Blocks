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

from blocks.engine.transformer import Transformer

if __name__ == "__main__":
      
    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    node = Node.load(name='basics_prototype',
                     ntype='prototype',
                     directory=BLOCK_PATH,)

    workflow = Workflow.load(
        name='workflow-test',
        ntype='workflow',
        directory=BLOCK_PATH,
        ignore_error=True
    )

    # ===============================================
    print("\n"+"="*40)

    transf = Transformer(
        rename_attr = [('result','n'),],
        modify_attr = [('n',3),],
        ignore_attr = []
    )

    with Workflow.create(stdout=sys.stdout) as wkc:

        wkc.import_node(
            node,
            'HC_node_1',
            transformer=None,
            method_name='basic_function' )

        wkc.import_node(
            node,
            'HC_node_2',
            transformer=transf,
            method_name='basic_function' )

        wkc.import_node(
            node,
            'HC_node_3',
            transformer=transf,
            method_name='basic_function' )

        wkc.import_node(
            node,
            'HC_node_4',
            transformer=transf,
            method_name='basic_function' )



        wkc.import_node(
            workflow,
            'HC_workflow_1',
            transformer=transf )
        
        wkc.add_link([('HC_node_1','HC_node_2')])
        wkc.add_link([('HC_node_1','HC_node_3')])
        wkc.add_link([('HC_node_2','HC_node_4')])
        wkc.add_link([('HC_node_3','HC_node_4')])
        wkc.add_link([('HC_node_4','HC_workflow_1')])

    wkc.execute(n=3)






