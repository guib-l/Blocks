from typing import *
from abc import *
from blocks.base import prototype 

from blocks.utils.logger import *



class Logical(prototype.Prototype):

    __ntype__ = "logical"

    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def forward(self, TYPE=None, **data):

        logger.warning(f"Executing Logicl function {TYPE}")

        func   = self.get_register_methods(name=TYPE).call
        output = func(**data)            
        
        return output













