import os
import sys
import time
from typing import *
from configs import *

from blocks import BLOCK_PATH

from blocks.base import *
from blocks.nodes.node import Node

from blocks.interface.interface import INTERFACE
from blocks.interface.communication import COMMUNICATE

from blocks.engine.transformer import Transformer



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

    # ================================================
    # Interface simple -> Ce que le module de communication remplace
    print("\n"+"="*40)

    interf_0 = INTERFACE.SIMPLE(node)
    print('Interface : ',interf_0)
    
    interf_1 = INTERFACE.SIMPLE(node)
    interf_2 = INTERFACE.SIMPLE(node)
    input_message = {'n': 2}
    print(f"Input Message: {input_message}")
    
    transform = Transformer(
        rename_attr = [('result','n'),],
        modify_attr = [('n',3),],
        ignore_attr = []
    )


    start = time.time()
    
    
    interf_0.input = input_message
    interf_0.execute()
    interf_1.input = interf_0.output
    interf_1.apply_transformer(transformer=transform)
    interf_1.execute()
    interf_2.input = interf_1.output
    interf_2.apply_transformer(transformer=transform)
    interf_2.execute()
    
    
    end = time.time()
    
    print(f'Final Output: {interf_2.output}')
    print(f'Interface executions completed in {end-start} s.')


    # ================================================
    # Communication interfaces direct par la mémoire python
    print("\n"+"="*40)


    from queue import Queue
    from blocks.interface.queue import DataQueue
    from blocks.engine.oriented import AcyclicGraphic

    links = [(1,'two'),('two',3)]
    graph = AcyclicGraphic(links=links, first=1, last=3)

    print('Graph : ',graph)

    comm_0 = COMMUNICATE.DIRECT(
        graphics=graph,
        interface=[(1,interf_0),
                   ('two',interf_1),
                   (3,interf_2)],
        queue=Queue()
    )
    print(comm_0)


    with comm_0 as comm:

        msg = {'n': 4}        
        comm.send(msg)

        for _node in comm.generator():
            
            try:
                _node.apply_transformer(transformer=transform)
            except Exception as e:
                print(f"Error applying transformer: {e}")

            _node.execute()

        received_msg = comm.receive()
        print(f"Received Message: {received_msg}")


    # ================================================
    # Communication interfaces direct par la mémoire python via une Queue Nominative
    print("\n"+"="*40)


    links = [(1,'two'),('two',3)]
    graph = AcyclicGraphic(links=links, first=1, last=3)

    print('Graph : ',graph)

    comm_0 = COMMUNICATE.LABEL(
        graphics=graph,
        interface=[(1,interf_0),
                   ('two',interf_1),
                   (3,interf_2)],
        queue=DataQueue()
    )
    print(comm_0)
    print('DataQueue : ',comm_0.queue._queue)

    with comm_0 as comm:

        msg = {'n': 4}        
        comm.send(msg)

        for _label,_node in comm.generator():
            
            try:
                _node.apply_transformer(transformer=transform)
            except Exception as e:
                print(f"Error applying transformer: {e}")

            _node.execute()

        received_msg = comm.receive()
        print(f"Received Message: {received_msg}")

    # ================================================
    # Communication asynchrone en mémoire python
    print("\n"+"="*40)

    










    