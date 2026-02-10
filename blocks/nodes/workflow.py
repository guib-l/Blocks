import os
import sys
import json

from typing import *
from abc import *
from pathlib import Path
from enum import Enum
import inspect

from queue import Queue

from blocks import BLOCK_PATH

from blocks.base import prototype
from blocks.engine import INSTALLER

from blocks.engine.environment import Environment
from blocks.engine.execute import Execute

from blocks.nodes.graphics import AcyclicGraph

from blocks.interface.queue import QUEUE
from blocks.interface.communication import COMMUNICATE 
from blocks.interface.interface import INTERFACE

from blocks.utils.exceptions import WorkflowError,ErrorCode
from blocks.utils.exceptions import safe_operation
from blocks.utils.logger import *

from blocks.engine.transformer import Transformer

class REGISTER_NODE:

    @staticmethod
    def import_node(
            node=None,
            ntype=None,
            directory=None,
            method_name=None,
            transformer=None,
            attributes = {}):
        
        assert node is not None, "Node instance must be provided."

        if isinstance(node, str):
            node = ntype.load(
                name=node,
                ntype=ntype.__name__.lower(),
                directory=directory
            )
        elif not isinstance(node, prototype.Prototype):
            logger.critical(f"Node {node} coudn't be loaded (wrong type)")
            
            raise WorkflowError(
                code=ErrorCode.WORKFLOW_ERROR_TYPE,
                message="The 'node' parameter must be a string or a Prototype instance.",
                details={"expected":prototype.Prototype,"current":type(node)}
            )
            
        if isinstance(transformer, dict):
            transformer = Transformer(**transformer)
        elif isinstance(transformer, Transformer):
            pass
        elif transformer is None:
            transformer = Transformer()
        else:
            logger.critical(f"Transformer {transformer} coudn't be loaded (wrong type)")
            
            raise WorkflowError(
                code=ErrorCode.WORKFLOW_ERROR_TYPE,
                message="The 'transformer' parameter must be a dict or a Transformer instance.",
                details={"expected":Transformer,"current":type(transformer)}
            )

        return {
            'node': node,
            'name': node.name,
            'directory': directory or node.directory,
            'function_name': method_name,
            'ntype': ntype,
            'transformer': transformer,
            'attributes': attributes,
        }

    @staticmethod
    def export_node(register_node):
        return {
            'node': register_node['node'].name,
            'directory': register_node['directory'],
            'ntype': register_node['ntype'].__name__.lower(),
            'method_name': register_node['function_name'],
            'transformer': register_node['transformer'].to_config() if register_node['transformer'] else None,
            'attributes': register_node['attributes'],
        }





class Workflow(prototype.Prototype):

    __ntype__ = "workflow"

    def __init__(
            self,
            register_nodes: Optional[Dict[str, Any]] = {},
            *,
            installer = None,
            environment = None,
            executor = None,
            graphics = None,
            communicate = None,
            interface = None,
            queue = None,
            **config
        ):

        self._register_nodes = {}
        self.set_register_nodes(register_nodes)
        logger.info("Loaded nodes into workflow")

        self._register_interface = []

        com_config   = config.pop('communicate_config',{})
        graph_config = config.pop('graphics_config', {})

        super().__init__(
            installer=installer,
            environment=environment,
            executor=executor,
            **config)

        self.graphics = graphics(**graph_config)
        logger.info("Build graphical workflow")

        self.queue = queue
        self.interface = interface

        self.set_register_interface()
        logger.info("Build interfaces of nodes")

        self.communicate = communicate



    # ===========================================
    # Graphics methods
    # ===========================================

    def add_link(self, origin, to_node=None):
        if isinstance(origin, list):
            self.graphics.add_links(origin)
        else:
            self.graphics.add_link(origin, to_node)
        
        self.communicate.update_graphics(self.graphics.graphics)

    def del_link(self, origin, to_node=None):
        if isinstance(origin, list):
            self.graphics.del_links(origin)
        else:
            self.graphics.del_link(origin, to_node)
        
        self.communicate.update_graphics(self.graphics.graphics)




    # ===========================================
    # Register Nodes and Interface
    # ===========================================
   
    def set_register_interface(self,):

        for label,register_node in self._register_nodes.items():
            
            self._register_interface.append(
                (label,
                 self.interface(
                     node=register_node['node'], 
                     name=register_node['function_name'],))
            )

        
    def get_register_nodes(self, name=None):

        if name is None:
            return self._register_nodes
        
        if name not in self._register_nodes.keys():
            raise WorkflowError(
                code=ErrorCode.WORKFLOW_REGISTER,
                message=f"Node '{name}' not found in registered nodes."
            )
        
        return self._register_nodes[name]

    def set_register_nodes(self, register_nodes: Dict[str, Any],):

        for label,register_node in register_nodes.items():
            _regist = REGISTER_NODE.import_node(**register_node)

            self._register_nodes[label] = _regist


    # ===========================================
    # Installater / Uninstaller
    # ===========================================


    def import_node(
            self,
            node,
            label,
            method_name=None,
            directory=None,
            transformer=None,
            interface=None,
            **kwargs):

        from blocks.base.prototype import Prototype
        assert isinstance(node, Prototype), \
            WorkflowError(
                code=ErrorCode.WORKFLOW_IMPORT_NODES,
                message='Input node needs to hinerit from prototype object'
            )

        _register = REGISTER_NODE.import_node(
            node=node,
            ntype=node.__ntype__,
            directory=directory or node.directory,
            method_name=method_name,
            transformer=transformer,
            attributes = kwargs
        )

        self._register_nodes[label] = _register

        if interface is None:
            interf = self.interface

        self._register_interface.append(
            (label, interf(node=node, name=method_name))
        )



    # ===========================================
    # Serialization methods
    # ===========================================


    def to_dict(self):

        with safe_operation(
                'dict serialisation',
                ErrorCode.WORKFLOW_SERIALIZE_ERR,
                WorkflowError ):
            
            _dict = super().to_dict()
            _dict.update({
                'installer':self.installer.__class__,
                'installer_config':self.installer.to_config(),
                'environment':self.environment.__class__,
                'environment_config':self.environment.to_config() or {},
                'executor':self.executor.__class__,
                'executor_config':self.executor.to_config() or {},
                'graphics':self.graphics.__class__,
                'graphics_config':self.graphics.to_config() or {},
                'registered_nodes':self._registred_nodes,
            })
            return _dict
    
    @classmethod
    def from_dict(cls, **data):
        with safe_operation(
                'dict deserialisation',
                ErrorCode.WORKFLOW_DESERIALIZE_ERR,
                WorkflowError ):
            
            return cls(**data)


    # ===========================================
    # Installater / Uninstaller
    # ===========================================

    def install(self, 
                **properties):
        
        assert hasattr(self.installer,'__install__'),\
            WorkflowError(
                code=ErrorCode.WORKFLOW_INSTALLER_ERR,
                message="Installer didn't have any __install__ method"
            )

        self.installer.__install__(**properties)

    def uninstall(self,
                  **properties):
        
        assert hasattr(self.installer,'__uninstall__'),\
            WorkflowError(
                code=ErrorCode.WORKFLOW_UNINSTALLER_ERR,
                message="Installer didn't have any __uninstall__ method"
            )
        
        self.installer.__uninstall__(**properties)


    # ===========================================
    # Load methods
    # ===========================================

    @classmethod
    def load(
            cls, 
            *,
            name:str,
            directory=None,
            format='json',
            ntype='prototype',
            installer=INSTALLER.WORKFLOW,
            **kwargs
        ):

        with safe_operation(
                'Loading workflow',
                ErrorCode.WORKFLOW_LOADING_ERR,
                ERROR=WorkflowError ):
            
            content, structure, register = installer.__load__(
                name=name,
                directory=directory,
                format=format,
                ntype=ntype,
            )
            content.update(**structure)
            content.update({
                'register_nodes': register
            })
            content.update(**kwargs)
            obj = cls(**content)
            print(f' \033[1;30m\u21BA {obj.__ntype__} loaded "{name}"\033[0m')
            return obj



    @classmethod
    def create(
            self,
            name:str='workflow-create',
            directory:Optional[str]=BLOCK_PATH,
            ntype:str='workflow',
            version:Optional[str]='0.0.1',
            stdout:Optional[TextIO]=sys.stdout,
            stderr:Optional[TextIO]=sys.stderr,
            mandatory_attr=False,
            metadata:Optional[Dict[str,Any]]={'source': 'generated'},
            installer=INSTALLER.WORKFLOW,
            installer_config:Optional[Dict[str,Any]]={'auto':False},
            environment=Environment,
            environment_config:Optional[Dict[str,Any]]={},
            executor=None,
            executor_config:Optional[Dict[str,Any]]={},
            graphics=AcyclicGraph,
            graphics_config:Optional[Dict[str,Any]]={},
            communicate=COMMUNICATE.LABEL,
            communicate_config:Optional[Dict[str,Any]]={},
            interface=INTERFACE.SIMPLE,
            queue=QUEUE.DATAQUEUE,
            **config
        ):


        with safe_operation(
                'Creating workflow',
                ErrorCode.WORKFLOW_CREATING_ERR,
                WorkflowError ):
            
            return Workflow(
                name=name,
                directory=directory,
                version=version,
                stdout=stdout,
                stderr=stderr,
                mandatory_attr=mandatory_attr,
                metadata=metadata,
                installer=installer,
                installer_config=installer_config,
                environment=environment,
                environment_config=environment_config,
                executor=executor,
                executor_config=executor_config,
                graphics=graphics,
                graphics_config=graphics_config,
                communicate=communicate,
                communicate_config=communicate_config,
                interface=interface,
                queue=queue,
                **config
            )


    def __enter__(self,):
        return self
    
    def __exit__(self, exc_type, exc_value, traceback):
        pass



    def draw(self, stdout=None):
        """Display the workflow graph in the terminal."""

        self.stdout = stdout or self.stdout
        #print(f"\n{'='*6}",self.stdout,sys.stdout)

        print(f"{'='*60}")
        print(f"\033[1;30m Workflow: {self.name} \033[0m")
        print(f"{'='*60}\n")
        
        # Display registered nodes
        print("Registered Nodes:")
        print("-" * 60)
        for label, reg_node in self._register_nodes.items():
            node_name = reg_node['node'].name
            node_type = reg_node['ntype'].__name__ if hasattr(reg_node['ntype'], '__name__') else str(reg_node['ntype'])
            method = reg_node.get('function_name', 'N/A')
            print(f"  [{label}] {node_name} (type: {node_type}, method: {method})")
        print("")
        
        # Display graph structure
        print("Graph Structure:")
        print("-" * 60)
        
        graph = self.graphics.graphics
        
        if not graph:
            print("  (empty graph)")
        else:
            # Display edges
            for origin, target in self.graphics.link:
                if target:
                    if isinstance(self._register_nodes[target]['node'], Workflow):
                        print(f"  {origin} --> Workflow({target})")
                    else:
                        print(f"  {origin} --> {target}")
                else:
                    print(f"  {origin} (no connections)")
        
        print(f"{'='*60}\n")

    @property
    def communicate(self):
        return self._communicate
    
    @communicate.setter
    def communicate(self, communicate):

        if communicate is None:
            self._communicate = COMMUNICATE.DIRECT

        try:
            self._communicate = communicate(
                graphics=self.graphics.graphics,
                interface=self._register_interface,
                queue=self.queue or Queue()
            )
        except Exception as e:
            raise WorkflowError(
                code=ErrorCode.WORKFLOW_COMMUNICATE,
                message="Communicate didn't work with Workflow",
                cause=e
            )


    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def execute(self, **data):
        
        logger.warning(f"Enter in {self.name} Workflow methods")

        error = False
        txt = "="*40
        print(f' \033[1;30m{txt}\033[0m')
        print(f" \u25B6\033[1;30m Executing Workflow '{self.name}'...\033[0m",
              file=sys.stdout)

        forward = getattr(self, 'forward', None)
        logger.info(f"Get forward Workflow methods")

        try:
            exec  = self.executor.execute(forward=forward)
            value = exec(**data)

        except Exception as e:
            logger.critical(f"Execution failed with message :\n{e}")

            error = True
            err =  WorkflowError(
                code=ErrorCode.WORKFLOW_EXECUTION,
                message=f"Execution failed with message :\n{e}",
                cause=e
            )
            if not self.ignore_error:
                raise err
        finally:
            txt = f"Execution {self.name} complete"

            if error:
                print(f' \u274C\033[1;30m {txt} (failed) \033[0m', 
                      file=sys.stdout)            
            else:
                print(f' \u2705\033[1;30m {txt} (succes) \033[0m', 
                      file=sys.stdout)
            
            logger.warning(f"Complete Workflow execution")

        txt = "="*40
        print(f' \033[1;30m{txt}\033[0m')
        sys.stdout = sys.__stdout__
        return value



    def forward(self, 
                name=None, 
                **data):

        with self.communicate as comm:
            
            comm.send(data)

            for _label,_node in comm.generator():

                _node._node.stdout = self.stdout
                _node._node.stderr = self.stderr
                
                transform = self._register_nodes.get(
                    _label, {}).get('transformer', None)
                
                if transform:
                    try:
                        _node.apply_transformer(transformer=transform)

                    except Exception as e:
                        logger.critical("Error applying transformer")

                        if not self.ignore_error:
                            raise WorkflowError(
                                code=ErrorCode.WORKFLOW_APPLY_TRANSFORMER,
                                message=f"Error applying transformer: {e}",
                                cause=e
                            )
                    
                _node.execute()

            received_msg = comm.receive()

        return received_msg





















