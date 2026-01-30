import os
import sys
import time
from typing import *
from configs import *


from blocks.base import *
from blocks.nodes.node import Node

from blocks.interface.datapacket import DataPacket,DataPacketPriority,DataPacketType

from blocks.interface.interface import INTERFACE



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














