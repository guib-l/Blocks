from typing import *

from blocks.interface.signal import Signal
from blocks.interface._interface import MESSAGE,MessageType
import node 


class Gate(node.Node):

    auth_inout = [ MessageType.DIRECT, ]


    default_node = {
        'interface':{
            'persistant':False,
            'restricted': False,
            'max_inp': 0,
            'max_out': 1,     
        }
    }

    def __init__(self,
                 transform: Optional[Callable[[Any], Any]] = None,
                 **kwargs) -> None:

        self.transform = transform

        super().__init__(**kwargs)

    def apply(self, **data) : 

        if self.transform:
            try:
                data = self.transform(**data)
            except Exception as e:
                return self.error(f"Transformation error: {e}")
        return data


    def feed(self, **data) -> Optional[MESSAGE]:

        data = self.apply(**data)

        # Create message
        msg = MESSAGE(
            FROM=self.id,
            TO=self._default_destination,
            TYPE=MessageType.DIRECT,
            DATA=data,
        )

        self.output = msg
        return self.output



