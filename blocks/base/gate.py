from typing import *

from blocks.base.signal import Signal
from blocks.socket.interface import MESSAGE,MessageType
import node 


class Gate(node.Node):

    auth_inout = [ MessageType.DIRECT, ]


    default_node = {
        'interface':{
            'persistant':False,
            'restricted': False,
            'lim_inp': (1,1),
            'lim_out': (1,1),            
        }
    }


    def feed(self, **data):
        '''
        feed
        
        Methods able to pass data to the next node

        args:
            data (dict): data into output  
        
        return: 
            none
        '''
        self.output = MESSAGE(DATA=data)




