import os,sys
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *
from blocks.base.dataset import DataSet
from blocks.base.baseBlock import BaseBlock



if __name__ == "__main__":
    
    # Create a sample dataset
    data = {
        'name': 'Sample-Dataset',
        'id': None,
        'values': [1, 2, 3, 4, 5],
        'metadata': {'source': 'generated', 'version': 1.0}
    }

    baseblock = BaseBlock(**data)

    print("BaseBlock instance created successfully.")
    print(baseblock)


    baseblock_bis = BaseBlock(**data)

    if baseblock==baseblock_bis:
        print("baseblock et baseblock_bis sont égaux")
    else:
        print("baseblock et baseblock_bis sont différents")


    