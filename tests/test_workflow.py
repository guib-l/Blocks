import os,sys
import time
from configs import *

from queue import Queue

from blocks.base import *
from blocks.base.prototype import export_metadata
from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow
from blocks.nodes.graphics import AcyclicGraphMixin

from blocks.interface.queue import QUEUE
from blocks.interface.communication import COMMUNICATE 
from blocks.interface.interface import INTERFACE

from blocks.base.prototype import INSTALLER

from blocks.engine.environment import EnvironMixin



# DONE TODO: Fonctionnement de workflow.forward
# DONE TODO: Méthode d'import/ajout de noeuds
# DONE TODO: Export des metadata minimum
# TODO: Enregistement des propriétés intrinsèques des node/workflow dans
# un objet pickle dédié
# TODO: Installation complète -> Vérification de l'existance des noeuds présents
# TODO: Correction bugs mineurs 



if __name__ == "__main__":
      
    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    start = time.time()
    node = Node.load(name='HC',
                     ntype='prototype',
                     directory=BLOCK_PATH)
    end = time.time()
    print(node)
    print("Node instance created successfully.")
    print(f'Instance created in {end-start} s.')

    #node.execute(n=5)

    # ===============================================
    # Lancement du workflow
    print("\n"+"*"*40)

   # Create a sample dataset
    data = {
        'name': 'HC_workflow',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'installer': INSTALLER.WORKFLOW,
        'mandatory_attr': False,
        'auto_create':True,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        #'environment': EnvironMixin,
        'executor': None,
        'graphics': AcyclicGraphMixin,
        'communicate': 'LABEL',
        'interface': 'SIMPLE',
        'queue': 'DATAQUEUE',
        'allowed_name':[],
        'links': [('HC_node_1','HC_node_2'), 
                  ('HC_node_2','HC_node_3')],
        'first': 'HC_node_1',
        'last': 'HC_node_3',
        'registered_nodes':{
            'HC_node_1': {'node':'HC', 
                          'directory':BLOCK_PATH,
                          'ntype':'node',
                          'transformer': None},
            'HC_node_2': {'node':node,
                          'name':node.name,
                          'function_name':'heavy_calculation',
                          'ntype':'prototype',
                          'transformer': lambda data: {'n': data['result']}},
            'HC_node_3': {'node':node,
                          'name':node.name,
                          'function_name':'heavy_calculation',
                          'ntype':'prototype',
                          'transformer': lambda data: {'n': data['result']}},
        }
    }

    wkw = Workflow(**data)
    print(wkw)
    print("Workflow instance created successfully.")
    print("\n"+"="*40)

    print(wkw.graphics)
    print("Workflow Graphics created successfully.")
    print("\n"+"="*40)

    print(wkw._registred_interface)
    print("Workflow Nodes registered successfully.")
    print("\n"+"="*40)



    wkw.execute(n=3)

    print("\n"+"="*40)
    export_metadata(wkw, 'workflow', 'json')

    results = wkw.to_dict()

    print('Registred : \n',results['registered_nodes'])

    new_wkw = Workflow.from_dict(**results)

    print(new_wkw)
    print(new_wkw.graphics)
    print(new_wkw.communicate)
    print(new_wkw.interface)


    new_wkw.execute(n=3)

    sys.exit()




    # ===============================================
    # Lancement du workflow
    print("\n"+"*"*40)

    workflow = Workflow.load(name='HC_workflow',
                              directory=BLOCK_PATH)
    print(workflow)
    print("Workflow instance created successfully.")

    ctx.import_node(node, 
                    label='HC_node_1', 
                    transformer=lambda data: {'n': data['results']})
    ctx.import_node(node, 
                    label='HC_node_2', 
                    transformer=lambda data: {'n': data['results']})
    ctx.import_node(node, 
                    label='HC_node_3', 
                    transformer=lambda data: {'n': data['results']})

    ctx.connect_nodes('HC_node_1', 'HC_node_2')
    ctx.connect_nodes('HC_node_2', 'HC_node_3')

    print("Workflow Context : \n",ctx)
    



    workflow.execute()






    sys.exit()






