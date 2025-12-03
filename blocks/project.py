import os
import sys

from blocks.interface._interface import (MessageType,MESSAGE,Interface)
from blocks.nodes.workflow import Workflow

class Project(Workflow):

    def __init__(self, 
                 global_interface=Interface, 
                 unique_interface=False,
                 **kwargs):

        super().__init__(_mandatory_attr=False, 
                         _interface=global_interface,
                         **kwargs)






