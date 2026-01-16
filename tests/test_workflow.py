import os,sys
import time
from configs import *

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.nodes.node import Node
from blocks.nodes.graphics import AcyclicGraph
from blocks.nodes.workflow import Workflow

from blocks.base.prototype import INSTALLER

from blocks.engine.environment import Environment

from blocks.interface.queue import QUEUE
from blocks.interface.communication import COMMUNICATE 
from blocks.interface.interface import INTERFACE


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

    node.execute(name='basic_function',n=5)


    # ===============================================
    def transf(data):
        return {'n': data['result']}

    # Lancement du workflow
    print("\n"+"*"*40)
    configuration = {
        'name': 'workflow-test',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'installer': INSTALLER.WORKFLOW,
        'installer_config':{
            'auto':False,
        },
        'environment': Environment,
        'environment_config':{},
        'executor': None,
        'executor_config':{},
        'graphics': AcyclicGraph,
        'graphics_config':{
            'links':[('HC_node_1','HC_node_2'), 
                     ('HC_node_2','HC_node_3')],
            'first':'HC_node_1',
            'last':'HC_node_3',
        },
        'communicate': COMMUNICATE.LABEL,
        'communicate_config':{},
        'interface': INTERFACE.SIMPLE,
        'queue': QUEUE.DATAQUEUE,
        'register_nodes':{
            'HC_node_1': {'node':'heavy_calculation', 
                          'directory':BLOCK_PATH,
                          'method_name':'heavy_calculation',
                          'ntype':Prototype,
                          'transformer': None},
            'HC_node_2': {'node':node,
                          'method_name':'basic_function',
                          'ntype':Prototype,
                          'transformer': transf},
            'HC_node_3': {'node':node,
                          'method_name':'basic_function',
                          'ntype':Prototype,
                          'transformer': transf},
        }
    }

    wk = Workflow(**configuration)
    print(wk)
    print("Workflow instance created successfully.")


    print(wk.graphics)
    print("Workflow Graphics created successfully.")
    
    
    # ===============================================
    print("\n"+"="*40)

    print("Registered nodes:")

    print(wk.get_register_nodes())
    print(wk.get_register_nodes(name='HC_node_1'))

    print(wk.communicate)

    wk.execute(n=3)

    wk.install()

    # ===============================================
    print("\n"+"="*40)
    
    new_wk = Workflow.load(
        name='workflow-test',
        directory=BLOCK_PATH,
        ntype="workflow",
    )
    print(new_wk)
    print("Workflow instance loaded successfully.")

    new_wk.execute(n=3)

    # ===============================================
    print("\n"+"="*40)

    wk.import_node(
        new_wk,
        'HC_workflow_1',
        transformer=transf )

    wk.add_link('HC_node_3','HC_workflow_1')

    print( 'Graphics: ',wk.graphics.graphics )

    wk.execute(n=3)

    wk.del_link('HC_node_3','HC_workflow_1')



    # ===============================================
    print("\n"+"="*40)

    with Workflow.create() as wkc:

        wkc.import_node(
            new_wk,
            'HC_workflow_1',
            transformer=None )


        wkc.import_node(
            new_wk,
            'HC_workflow_2',
            transformer=transf )
        
        wkc.add_link([('HC_workflow_1','HC_workflow_2')])

    wkc.execute(n=2)

    wkc.draw()



    sys.exit()




