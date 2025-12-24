import os,sys
import time
from configs import *

from blocks.base import *
from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.nodes.graphics import AcyclicGraphMixin

from blocks.base.prototype import INSTALLER

from blocks.engine.environment import EnvironMixin





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

    node.execute(n=5)

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
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'environment': EnvironMixin,
        'executor': None,
        'graphics': AcyclicGraphMixin,
        'links': [('HC_node_1','HC_node_2'), 
                  ('HC_node_2','HC_node_3')],
        'first_node': 'HC_node_1',
        'last_node': 'HC_node_3',
        'nodes':{
            'HC_node_1': node,
            'HC_node_2': node,
            'HC_node_3': node,
        }
    }

    wkw = Workflow(**data)
    print(wkw)
    print("Workflow instance created successfully.")

    print(wkw.graphics)
    print("Workflow Graphics created successfully.")

    print(wkw._registred_nodes)
    print("Workflow Nodes registered successfully.")

    print("Workflow executor : \n",wkw.executor)


    wkw.execute()



    sys.exit()

    # ===============================================
    # Lancement du workflow
    print("\n"+"*"*40)

    workflow = Workflow.load(name='HC_workflow',
                              directory=BLOCK_PATH)
    print(workflow)
    print("Workflow instance created successfully.")

    ctx.import_node(node, label='HC_node_1')
    ctx.import_node(node, label='HC_node_2')
    ctx.import_node(node, label='HC_node_3')

    ctx.connect_nodes('HC_node_1', 'HC_node_2')
    ctx.connect_nodes('HC_node_2', 'HC_node_3')

    print("Workflow Context : \n",ctx)
    


    workflow.input = {'n':4}

    workflow.execute()






    sys.exit()






