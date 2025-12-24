import os
import time
from configs import *

from blocks.base import *
from blocks.base.prototype import Prototype
from blocks.base.prototype import export_metadata

from blocks.base.prototype import INSTALLER

from blocks.export import task_node
from blocks.engine.environment import EnvironMixin


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
    

    # Tests des methods -----------------------------
    print('Register : \n',proto._register_methods)

    method_01 = proto.get_register_methods('say')
    method_01.call('Hello')

    print('Register : \n',proto._register_methods)

    proto.export_method("export.py", 
                        BLOCK_PATH, 
                        **proto._register_methods)

    proto.import_method( os.path.join(BLOCK_PATH,"export.py") )
    print('Register : \n',proto._register_methods)

    # Tests de l'installation -----------------------
    proto = Prototype.install( **data )
    print(proto)
    print("Prototype instance installed successfully.")
    

    proto.uninstall()
    print("Prototype instance uninstalled successfully.")




    # ===============================================
    # Installation d'un Prototype via l'appel de @task
    print("\n"+"*"*40)

    hc = heavy_calculation()
    print(hc)

    results = hc.execute(n=3)
    print('Results : ',results)
    
    from blocks.base.prototype import Install
    Install(hc,name='HC',directory=BLOCK_PATH)

    del hc
    
    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    proto = Prototype.load(name='HC',
                           ntype='prototype',
                           directory=BLOCK_PATH)
    print(proto)
    print("Prototype instance created successfully.")

    print(proto._register_methods)

    # Ajout d'une méthode d'éxecution par défaut
    proto.execute(n=6)


    # ===============================================
    # Manipulation du prototye (déplacement, nom, suppr ...)
    print("\n"+"*"*40)

    # TODO: Déplacer les fichiers (avec l'environnement ?)

    # TODO: Changer le nom

    # TODO: Supprimer les fichiers (facultatif)


    # ===============================================
    # Ajouter un environment et un executor indépendant (qui devra être
    # sauvegardé dans un fichier pickle / json suivant ce qui sera le plus 
    # simple à le re-load)
    print("\n"+"*"*40)










