import os
import time
from configs import *

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.base.prototype import INSTALLER

from blocks.export import task_node
from blocks.engine.environment import Environment


def basic_function(n=5):
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result


@task_node(backend    = 'default',
           execute    = None,
           objectType = Prototype,)
def heavy_calculation(n=5):
    """Fonction qui sera interruptible (environ)."""
    result = 0
    for i in range(n):
        # Simulation de calcul lourd
        result += i
        time.sleep(0.2)
        print(f"Calcul en cours... étape {i+1}/{n}")
    return result



if __name__ == "__main__":
      
   # Create a sample dataset
    data = {
        'name': 'prototype-test',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'installer': INSTALLER.PYTHON,
        'installer_config':{
            'auto':True,
        },
        'environment': Environment,
        'environment_config':{},
        'executor': None,
        'executor_config':{},
    }


    # ===============================================
    # Initialisation d'un Prototype
    print("\n"+"*"*40)

    print("BUILD PROTOTYPE in-place")
    
    proto = Prototype(**data)

    print(proto)
    print("Prototype instance created successfully.") 


    # ===============================================
    # Installation COMPLET d'un Prototype via 'install'
    print("\n"+"*"*40)

    data.update(
        {
            'files':['myscript/my_script.py',],
            'methods':[basic_function],
            'allowed_name':[]
        }
    )

    proto = Prototype(**data)
    print(proto)
    print("Prototype instance created successfully.") 

    proto.install()
    print("Prototype instance installed successfully.")



    new_proto = Prototype.load(
        name='prototype-test',
        directory=BLOCK_PATH,
        format='json',
        ntype='prototype'
    )

    print(new_proto)
    print("Prototype instance loaded successfully.")


    proto.uninstall()
    print("Prototype instance uninstalled successfully.")


    # Re-installation pour test @task_manager
    proto = Prototype(**data)
    print(proto)
    print("Prototype instance created successfully.") 

    proto.install()

    # ===============================================
    # Prototype vie @task_manager
    print("\n"+"*"*40)


    hc = heavy_calculation()
    print(hc)

    # TODO : Uncomment to test installation via task manager
    hc.install(directory=BLOCK_PATH)


    results = hc.execute(n=4)
    print('Results : ',results)
    

    proto.execute(name='say', words='from Prototype execute method')

    
    # ===============================================
    # Manipulation du prototye (déplacement, nom, suppr ...)
    print("\n"+"*"*40)

    # Déplacer les fichiers (avec l'environnement ?)
    proto.installer.move( os.path.join(BLOCK_PATH, '..'), erase_source=True )
    proto.installer.move( BLOCK_PATH, erase_source=True )

    # Changer le nom
    proto.installer.rename('HC')

    new_proto = Prototype.load(
        name='HC',
        directory=BLOCK_PATH,
        format='json',
        ntype='prototype'
    )

    print(new_proto)
    print("Prototype instance loaded successfully.")

    # Compression d'un prototype
    new_proto.installer.compress( )
    print("Prototype instance compressed successfully.")

    print(new_proto.installer.path_to_install)


    new_proto.uninstall()
    print("Prototype instance uninstalled successfully.")

    # Décompression d'un prototype
    new_proto.installer.decompress()
    print("Prototype instance decompressed successfully.")

    new_proto = Prototype.load(
        name='HC',
        directory=BLOCK_PATH,
        format='json',
        ntype='prototype'
    )

    print(new_proto)
    print("Prototype instance loaded successfully.")

    new_proto.execute(name='basic_function', n=3)


