import os,sys
import time
from configs import *

from blocks import BLOCK_PATH

from blocks.base import *
from blocks.base.prototype import Prototype

from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.engine.execute import Execute
from blocks.engine.oriented import AcyclicGraphic,CyclicGraphic
from blocks.engine import INSTALLER

from blocks.engine.environment import Environment

from blocks.interface.buffer import BUFFER
from blocks.interface.communication import COMMUNICATE 
from blocks.interface.interface import INTERFACE

from blocks.utils.logger import logger

from blocks.engine.transformer import Transformer

if __name__ == "__main__":
      
    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    start = time.time()
    node = Node.load(name='basics_prototype',
                     ntype='prototype',
                     directory=BLOCK_PATH,)
    end = time.time()
    print(node)
    print("Node instance created successfully.")
    print(f'Instance created in {end-start} s.')

    node.execute(name='basic_function',n=5)


    # ===============================================
    def transf(data):
        if data['result']==0:
            return {'n':None}
        return {'n': data['result']}
    
    

    transf = Transformer(
        rename_attr = [('result','n'),],
        modify_attr = [],
        ignore_attr = []
    )

    # Lancement du workflow
    print("\n"+"*"*40)
    configuration = {
        'name': 'workflow-test',
        'id': None,
        'version': '0.0.1',
        'stdout': sys.stdout,
        'stderr': sys.stderr,
        'ignore_error':False,
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
        'executor': Execute,
        'executor_config':{},
        'graphics': AcyclicGraphic,
        'graphics_config':{
            'links':[('HC_node_1','HC_node_2'), 
                     ('HC_node_2','HC_node_3')],
            'first':'HC_node_1',
            'last':'HC_node_3',
        },
        'communicate': COMMUNICATE.LABEL,
        'communicate_config':{},
        'interface': INTERFACE.SIMPLE,
        'buffer': BUFFER.DATABUFFER,
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
                          'transformer': transf.to_config()},
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
    #sys.exit()

    # ===============================================
    print("\n"+"="*40)

    wk.import_node(
        new_wk,
        'HC_workflow_1',
        transformer=transf )

    wk.add_link('HC_node_3','HC_workflow_1')
    wk.graphics.build()
    print( 'Graphics: ',wk.graphics.graphics )

    #wk.execute(n=3)

    #wk.del_link('HC_node_3','HC_workflow_1')


    # ===============================================
    print("\n"+"="*40)

    with Workflow.create(stdout=sys.stdout) as wkc:

        wkc.import_node(
            new_wk,
            'HC_workflow_1',
            transformer=None )


        wkc.import_node(
            new_wk,
            'HC_workflow_2',
            transformer=transf )
        
        wkc.add_link([('HC_workflow_1','HC_workflow_2')])

    wkc.execute(n=3)

    wkc.draw()

    #sys.exit()


    # ===============================================
    print("\n"+"="*40)

    with Workflow.create(stdout=sys.stdout,
                         graphics=CyclicGraphic) as wkc:

        wkc.import_node(
            new_wk,
            'HC_workflow_1',
            transformer=None )


        wkc.import_node(
            new_wk,
            'HC_workflow_2',
            transformer=transf )
        
        wkc.add_link([('HC_workflow_1','HC_workflow_2')])

        wkc.import_node(
            node,
            'HC_node_1a',
            method_name="basic_function",
            transformer=transf )
        
        wkc.add_link([('HC_workflow_2','HC_node_1a')])

        wkc.import_node(
            node,
            'HC_node_2b',
            method_name="basic_function",
            transformer=transf )
        
        wkc.add_link([('HC_node_1a','HC_node_2b')])

        wkc.add_loop(
            start='HC_node_1a',
            end='HC_node_2b',
            epoch=2,
            ctype='FOR'
        )


    wkc.execute(n=3)


    sys.exit()




