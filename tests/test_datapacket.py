import os
import sys
import time
from copy import copy, deepcopy
from typing import *
from configs import *

from blocks.nodes.node import Node
from blocks.base import *

from blocks.interface.interface import Interface
from blocks.interface.datapacket import (DataPacket,
                                         #DataPacketQueue,
                                         DataPacketPriority,
                                         DataPacketType)
from blocks.base.prototype import Prototype

from blocks.interface.buffer import DataBuffer

from blocks import BLOCK_PATH



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



    input_message = DataPacket(
        FROM=0,
        TO=1,
        TYPE=DataPacketType.DIRECT,
        SUBJECT="Test Message",
        PRIORITY=DataPacketPriority.HIGH,
        DATA={"n": 5}
    )

    print(f"Input Message: {input_message}")



    err_message = DataPacket.generate_error(
        FROM=node.id,
        error="This is a test error message.",
        DATA = dict(
            additional_info={"detail": "Additional error details."},
            error_code=404,),
        PRIORITY=DataPacketPriority.HIGH,   
    )

    print(f'Generated Error Message: {err_message}')


    msg_1 = DataPacket.generate_message(
        FROM=node.name,
        TO=2,
        DATA={"value": 42},
        SUBJECT="Computation Result",
        PRIORITY=DataPacketPriority.NORMAL
    )
    msg_2 = DataPacket.generate_message(
        FROM=node.name,
        TO=3,
        DATA={"value": 42},
        SUBJECT="Computation Result",
        PRIORITY=DataPacketPriority.NORMAL
    )

    queue = DataBuffer()
    queue.enqueue(msg_1)
    queue.enqueue(msg_2)

    print(f"Queue after enqueuing messages: {queue}")

    msg_to_get = queue.peek_by_property(
        all_results=True, TO=2, SUBJECT="Computation Result")
    
    print(f"Messages peeked by property: {msg_to_get}")

    msg_to_send = queue.dequeue_by_property(
        all_results=True, SUBJECT="Computation Result")

    print(f"Message dequeued by property: {msg_to_send}")

    queue.enqueue(msg_1)
    queue.enqueue(msg_2)

    dequeued_msg = queue.dequeue()
    print(f"Dequeued Message: {dequeued_msg}")


