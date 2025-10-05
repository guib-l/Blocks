from typing import *

from blocks.base.signal import Signal
from blocks.socket.interface import MESSAGE,MessageType
import node 



Workflow = TypeVar('Workflow', bound='Workflow')



class Workflow(node.Node):

    auth_inout = [ MessageType.DIRECT, ]

    default_node = {
        'interface':{
            'persistant':False,
            'restricted': False,
            'max_inp': 999,
            'max_out': 999,          
        }
    }

    def __init__(self, 
                 graphics = None,
                 **kwargs):

        self.graphics = graphics

        super().__init__(**kwargs)

    def add_node(self, node: node.Node):
        ...

    def remove_node(self, node_id: str):
        ...

    def connect_nodes(self, from_node: str, to_node: str):
        ...

    def disconnect_nodes(self, from_node: str, to_node: str):
        ...

    







    