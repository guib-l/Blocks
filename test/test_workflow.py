
from configs import *


import pytest

from blocks.nodes.workflow import Workflow

from blocks.engine.oriented import AcyclicGraphic
from blocks.engine.installer import Installer
from blocks.engine.execute import Execute
from blocks.engine.environment import Environment
from blocks.interface.communication import COMMUNICATE
from blocks.interface.interface import INTERFACE
from blocks.interface.buffer import BUFFER

BLOCK_PATH  = "myblock/"
INSTALL     = Installer
EXECUTE     = Execute
ENVIRONMENT = Environment

data = {
        'name': 'workflow-test',
        'id': None,
        'version': '0.0.1',
        'directory':BLOCK_PATH,
        'mandatory_attr': False,
        'metadata': {'source': 'generated', 
                     'version': 1.0,
                     'description': 'A sample dataset for testing'},
        'installer': INSTALL,
        'installer_config':{
            'auto':False,
        },
        'graphics': AcyclicGraphic,
        'graphics_config':{},
        'communicate': COMMUNICATE.LABEL,
        'communicate_config':{},
        'interface': INTERFACE.SIMPLE,
        'buffer': BUFFER.DATABUFFER,
        'environment': ENVIRONMENT,
        'environment_config':{},
        'executor': EXECUTE,
        'executor_config':{},
        'register_nodes':{},
    }

class TestWorkflowInitialization:
    """Test Workflow initialization and properties."""
     
    def test_workflow(self):
        """Test Workflow initialization and properties."""

        workflow = Workflow(**data)
        
        assert workflow.name == 'workflow-test'
        assert workflow.version == '0.0.1'
        assert workflow.directory == "myblock/"

        assert isinstance(workflow.environment, Environment)
        assert isinstance(workflow.installer, Installer)
        assert isinstance(workflow.executor, Execute)

    def test_workflow_graphics(self):
        """Test Workflow graphics initialization and properties."""

        link = [ ('g',2),(4,1),(0,'g'),
                (2,4),(2,54),(3,4),(7,54),
                ('g',3),(54,8),(3,8) ]
        data['graphics_config'] = {
            'links':link,
            'first':0,
            'last':None,
        }
        workflow = Workflow(**data)
        assert isinstance(workflow.graphics, AcyclicGraphic)
        assert len(workflow.graphics.nodes) == 9

    def test_workflow_register_nodes(self):
        """Test Workflow register nodes initialization and properties."""
        from blocks.base.prototype import Prototype

        try:
            proto = Prototype.load(
                name='prototype-file-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."

        data['register_nodes'] = {
            'HC_node_1': {'node':'prototype-file-test', 
                          'directory':BLOCK_PATH,
                          'method_name':'heavy_calculation',
                          'ntype':Prototype,
                          'transformer': None},
            'HC_node_2': {'node':proto,
                          'method_name':'say',
                          'ntype':Prototype,
                          'transformer': None},
            'HC_node_3': {'node':proto,
                          'method_name':'say2',
                          'ntype':Prototype,
                          'transformer': None},
        }

        workflow = Workflow(**data)

        assert len(workflow.get_register_nodes()) == 3
    
    def test_workflow_execution(self):
        """Test Workflow execution."""
        from blocks.base.prototype import Prototype

        try:
            proto = Prototype.load(
                name='prototype-file-test',
                directory=BLOCK_PATH,
                format='json',
                ntype='prototype')
            loaded = True
        except Exception as e:
            print(f"Loading failed: {e}")
            loaded = False
        
        assert loaded, "Prototype loading should succeed."

        links = [ ('HC_node_1','HC_node_2'), ]
        data['graphics_config'] = {
            'links':links,
            'first':'HC_node_1',
            'last':None,
        }

        data['register_nodes'] = {
            'HC_node_1': {'node':'prototype-file-test', 
                          'directory':BLOCK_PATH,
                          'method_name':'say2',
                          'ntype':Prototype,
                          'transformer': None},
            'HC_node_2': {'node':proto,
                          'method_name':'say',
                          'ntype':Prototype,
                          'transformer': None},
        }

        workflow = Workflow(**data)

        workflow.execute(n='hello')







