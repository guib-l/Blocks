import os
import sys
import time
import asyncio
from copy import copy, deepcopy
from typing import *
from configs import *


from blocks.base import *
from blocks.nodes.node import Node

from blocks.interface.datapacket import DataPacket,DataPacketPriority,DataPacketType
from blocks.base.prototype import Prototype

from blocks.interface.interface import INTERFACE





class COMMUNICATE:

    def send(self,):
        pass

    def receive(self,):
        pass



from blocks.nodes.graphics import GRAPHICS  

class ORCHEST:

    def __new__(cls, **kwargs):
        com = kwargs.get('communicate', COMMUNICATE)
        
        cls = type(
            cls.__name__,
            (com, cls),
            {}
        )
        return super().__new__(cls)
    
    def __init__(self,
                 interface=INTERFACE,
                 communicate=COMMUNICATE,
                 runner=GRAPHICS):
        
        self.runner = runner()

        self._interface = interface
        self._communicate = communicate
    
    def add_node(self, node:Prototype, label:Optional[str]=None):
        inode = self._interface(node)
        self.runner.add_node(inode, label=label)

    def add_nodes(self, *nodes:Prototype):
        for node in nodes:
            inode = self._interface(node)
            self.runner.add_node(inode)
    
    def add_link(self, from_idx:int, to_idx:int):
        self.runner.add_link(from_idx, to_idx)

    def add_links(self, links:List[Tuple[int,int]]):
        for link in links:
            self.runner.add_link(link[0], link[1])

    def swap(self, idx_1:int, idx_2:int):
        self.runner.swap(idx_1, idx_2)



    def pre_build(self,):
        self.runner.build()

        for node in self.runner.graphics:
            interface = INTERFACE(node)
            self._register_interface[node.name] = interface

        for from_node, to_node in self.runner.link:
            from_interface = self._register_interface[from_node.name]
            to_interface   = self._register_interface[to_node.name]

            message = from_interface.execute()
            to_interface.receive(message)


    def run(self,):
        

        for node_name, interface in self._register_interface.items():
            output_message = interface.send()
            print(f"Output from node {node_name}: {output_message}")





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

    # ================================================
    # Interface simple
    print("\n"+"="*40)

    interf_0 = INTERFACE.SIMPLE(node)
    print('Interface : ',interf_0)

    interf_1 = INTERFACE.SIMPLE(node)
    interf_2 = INTERFACE.SIMPLE(node)

    input_message = {'n': 5}
    print(f"Input Message: {input_message}")

    transform = lambda data : {'n': min(data['result'],9)}

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
    print(f'Message assigned in {end-start} s.')


    # ===============================================
    # Interface avancée
    print("\n"+"="*40)

    input_message_1 = DataPacket(
        FROM=0,
        TO=1,
        TYPE=DataPacketType.DIRECT,
        SUBJECT=node.name,
        PRIORITY=DataPacketPriority.HIGH,
        DATA={"n": 7}
    )
    input_message_2 = DataPacket(
        FROM=-1,
        TO=1,
        TYPE=DataPacketType.DIRECT,
        SUBJECT=node.name,
        PRIORITY=DataPacketPriority.HIGH,
        DATA={"n": 8}
    )
    input_message_3 = DataPacket(
        FROM=-2,
        TO=1,
        TYPE=DataPacketType.DIRECT,
        SUBJECT=node.name,
        PRIORITY=DataPacketPriority.HIGH,
        DATA={"n": 8, 'k':5},
        TRANSFORM=None  
    )

    print(f"Input Message: {input_message_1}")

    start = time.time()
    InterIO = INTERFACE.ADVANCED(node, ignore_conflict=True, ignore_keys=[])
    print('Interface : ',InterIO)

    InterIO.input = input_message_1
    InterIO.input = input_message_2
    InterIO.input = input_message_3

    end = time.time()
    print(f'Instance and message created in {end-start} s.')

    print("\n"+"="*40)
    print("Input from Interface:", InterIO.input)
    print("Executing Node via Interface...")

    start = time.time()
    InterIO.execute(delay=0.,
                    transformer=lambda data: {d:v for d,v in data.items() if d=='n'})
    end = time.time()
    print(f'Execution completed in {end-start} s.')

    InterIO.product_output(TO=2)
    print("Output from Interface:", InterIO.output)

    sys.exit()


    # ===============================================
    # Orchestrator

    orchestrator = ORCHEST()

    orchestrator.add_node(node)
    orchestrator.add_node([node,])
    orchestrator.add_nodes(node,node)
    orchestrator.add_node(node, label="node_X")

    print('List of all nodes : ',orchestrator.nodes)
    
    idx_1,idx_2 = 2,4
    orchestrator.swap(idx_1, idx_2)

    print('List of all nodes : ',orchestrator.nodes)

    orchestrator.add_link(0,1)

    links = [(1,2),(2,3),(3,4),(4,'node_X')]
    orchestrator.add_links(links)

    # Méthode qui sert à améliorer l'exécution : elle 
    # pré-construit l'ensemble des message entre les différentes
    # fonctions à executer 
    orchestrator.pre_build()

    orchestrator.run()












