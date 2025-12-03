import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.nodes.node import Node
from blocks.base import *

from blocks.interface._interface import (MessageType,MESSAGE,Interface)


class Environment:
    ... # Placeholder for environment methods 
    # could include setup, teardown, config management, etc.


class Executor:
    # Placeholder for executor methods 
    # could include task execution, job management, etc.
    ... 

if __name__ == "__main__":

  
    # Initialisation d'un Block
    node1 = Node.load(name='function-test',
                      directory=BLOCK_PATH)
    print(node1)
    node2 = Node.load(name='function-test',
                      directory=BLOCK_PATH)
    print(node2)
    node3 = Node.load(name='function-test',
                      directory=BLOCK_PATH)
    print(node3)

    print("Nodes instance created successfully.")


    interface1 = Interface(node=node1)
    interface2 = Interface(node=node2)
    interface3 = Interface(node=node3)

    msg = MESSAGE(FROM=node1.id, 
                  TO=node2.id, 
                  SUBJECT="test_subject", 
                  DATA={"key": "value"})
    result = interface2.receive(msg,1)
    print(result)



    msgs = [
            MESSAGE(FROM=node2.id, 
                    TO=node3.id, 
                    SUBJECT="subject1", 
                    DATA={"key1": "value1"}),
            MESSAGE(FROM=node2.id, 
                    TO=node3.id, 
                    SUBJECT="subject2", 
                    DATA={"key2": "value2"}),
            MESSAGE(FROM=node2.id, 
                    TO=node3.id, 
                    SUBJECT="subject3", 
                    DATA={"key3": "value3"})
        ]


    results = interface3.receive(msgs)
    print(results)
    print("Messages received successfully.")

    interface3.provide('key1', 'value_1',output_index=0)
    interface3.provide('key2', 'value_2',output_index=1)
    print(interface3.output)
    print("Messages provided successfully.")


    # Test sending multiple messages
    msgs = [
            MESSAGE(FROM=node1.id, 
                    TO=node2.id, 
                    SUBJECT="subject1", 
                    DATA={"key1": "value1"}),
            MESSAGE(FROM=node1.id, 
                    TO=node2.id, 
                    SUBJECT="subject2", 
                    DATA={"key1": "value2"}),
            ]
    
    results = interface1.send(msgs)
    print(results)
    print("Messages sent successfully.")

    interface2.input = msgs
    print("Interface input set successfully.")

    interface1.output = msgs
    print("Interface output set successfully.")

    mrg = interface1.merge()
    print("Merged DATA:", mrg)
    print("Messages merged successfully.")

    interface2.clear_register()
    print("Interface register cleared successfully.")

    interface1.clear_outputs()
    print("Interface outputs cleared successfully.")


    intdict = interface1.to_dict()
    print(intdict)





