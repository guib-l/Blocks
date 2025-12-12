import os,sys
import time
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *
from blocks.base.dataset import DataSet
from blocks.base.block import Block

from blocks.base import *
from blocks.base.prototype import Prototype
from blocks.base.prototype import export_metadata

from blocks.engine.python_install import _python_installer

from blocks.base.prototype import INSTALLER

from blocks.export import task_node


def basic_function(n=5):
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result


@task_node(backend    = 'default',
           directory  = BLOCK_PATH,
           execute    = None,
           objectType = Prototype,)
def heavy_calculation(n=5):
    """Fonction qui sera interruptible."""
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result


from blocks.engine.environment import EnvironMixin

if __name__ == "__main__":
      
   # Create a sample dataset
    data = {
        'name': 'prototype-test',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'installer': INSTALLER.DEFAULT,
        'mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'environment': EnvironMixin,
        'executor': None,
    }
  
    # ===============================================
    # Initialisation d'un Prototype
    print("\n"+"*"*40)

    print("BUILD PROTOTYPE in-place")
    
    proto = Prototype(auto_create=True,
                      **data)
    print(proto)
    print("Prototype instance created successfully.") 

    # TODO: 'directory' -> path absolu du repertoire
    # TODO: 'files' -> path absolu/relatif ?
    # TODO: 'codes' -> nom des fonction qui sont transformés en objet 
    # lorsqu'il sont récupérés 

    export_metadata(proto, 'prototype', 'json')

    # Load de l'objet à partir du répertoire
    proto = Prototype.load(name='prototype-test',
                           ntype='prototype',
                           directory=BLOCK_PATH)
    print(proto)
    print("Prototype instance created successfully.")

    proto.delete_directory()


    # ===============================================
    # Installation COMPLET d'un Prototype via 'install'
    print("\n"+"*"*40)

    data.update(
        {'auto_create':False,
         'installer':INSTALLER.PYTHON,
         'methods':[basic_function,],
         'files':['myscript/my_script.py',],}
        )

    proto = Prototype(**data)
    print(proto)

    print(proto._register_methods)

    method_01 = proto.get_register_methods('say')
    method_01.call('Hello')

    print(proto._register_methods)

    proto.export_method("export.py", 
                        BLOCK_PATH, 
                        **proto._register_methods)

    proto.import_method( os.path.join(BLOCK_PATH,"export.py") )

    print(proto._register_methods)




    proto = Prototype.install( **data )
    print(proto)
    print("Prototype instance installed successfully.")
    

    proto.uninstall()
    print("Prototype instance uninstalled successfully.")




    # ===============================================
    # Installation d'un Prototype via l'appel de @task
    print("\n"+"*"*40)

    results = heavy_calculation()
    print(results)


    sys.exit()


    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    proto = Prototype.load(name='task_heavy_calculation',
                           ntype='prototype',
                           directory=BLOCK_PATH)
    print(proto)
    print("Prototype instance created successfully.")

    proto.execute(n=3)


    # ===============================================
    # Manipulation du prototye (déplacement, nom, suppr ...)
    print("\n"+"*"*40)








