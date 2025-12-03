from typing import *

from blocks.base.signal import Signal
from blocks.interface._interface import MESSAGE,MessageType
import node 


class TriggerType(str, Enum):
    EVENT = "event"           # Triggered by specific event
    TIME = "time"             # Triggered at specific time
    INTERVAL = "interval"     # Triggered at regular intervals
    CONDITION = "condition"   # Triggered when condition is met
    SIGNAL = "signal"         # Triggered by external signal
    DATA = "data"             # Triggered by data pattern
    MANUAL = "manual"         # Manually triggered

class Trigger(node.Node):

    auth_inout = [ MessageType.DIRECT, ]


    default_node = {
        'interface':{
            'persistant':False,
            'restricted': False,
            'max_inp': 1,
            'max_out': 1,     
        }
    }

    def __init__(self, 
                 trigger_type: TriggerType = TriggerType.MANUAL,
                 auto_start: bool = False,
                 cooldown: int = 0,
                 **kwargs):

        self.trigger_type = trigger_type
        self.auto_start = auto_start
        self.cooldown = cooldown

        super().__init__(**kwargs)

        # Auto-start if configured
        if auto_start and self.trigger_type != TriggerType.MANUAL:
            self.start_watching()


    def trigger(self, **data):
        ...

    def start_watching(self):
        ...

    def stop_watching(self):
        ...
    





