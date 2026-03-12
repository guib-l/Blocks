
from typing import *
from abc import *
from blocks.base import prototype 

from blocks.utils.logger import *

    

class Node(prototype.Prototype):

    __ntype__ = "node"

    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def forward(self, name=None, **data):

        logger.warning("Executing function in Node forward method")

        #with self.environment as env:

        func   = self.get_register_methods(name=name).call
        output = func(**data)
        
        logger.warning(f"Successful Node execution")
        
        return output

















