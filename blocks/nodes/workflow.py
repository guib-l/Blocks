import os
import sys
import json

from typing import *
from abc import *
from pathlib import Path
from enum import Enum
import inspect

from queue import Queue

from blocks.base import prototype
from blocks.base import BLOCK_PATH
from blocks.base.prototype import INSTALLER

from blocks.engine.environment import Environment
from blocks.engine.execute import Execute

from blocks.nodes.graphics import AcyclicGraph

from blocks.interface.queue import QUEUE
from blocks.interface.communication import COMMUNICATE 
from blocks.interface.interface import INTERFACE






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
            raise TypeError(
                "The 'node' parameter must be a string or a Prototype instance.")
        
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
            'transformer': register_node['transformer'],
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

        self._register_interface = []

        com_config   = config.pop('communicate_config',{})
        graph_config = config.pop('graphics_config', {})

        super().__init__(
            installer=installer,
            environment=environment,
            executor=executor,
            **config)

        self.graphics = graphics(**graph_config)

        self.queue = queue
        self.interface = interface

        self.set_register_interface()

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
            raise KeyError(f"Node '{name}' not found in registered nodes.")
        
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
            TypeError('Input node needs to hinerit from prototype object')

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
        return cls(**data)


    # ===========================================
    # Installater / Uninstaller
    # ===========================================

    def install(self, 
                **properties):

        self.installer.__install__(**properties)

    def uninstall(self,
                  **properties):
        
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

        content, structure, register = installer.__load__(
            name=name,
            directory=directory,
            format=format,
            ntype=ntype,
            **kwargs
        )
        content.update(**structure)
        content.update({
            'register_nodes': register
        })
        return cls(**content)


    @classmethod
    def create(
            self,
            name:str='workflow-create',
            directory:Optional[str]=BLOCK_PATH,
            ntype:str='workflow',
            version:Optional[str]='0.0.1',
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

        return Workflow(
            name=name,
            directory=directory,
            version=version,
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



    def draw(self):
        """Display the workflow graph in the terminal."""
        print(f"\n{'='*60}")
        print(f"Workflow: {self.name}")
        print(f"{'='*60}\n")
        
        # Display registered nodes
        print("Registered Nodes:")
        print("-" * 60)
        for label, reg_node in self._register_nodes.items():
            node_name = reg_node['node'].name
            node_type = reg_node['ntype'].__name__ if hasattr(reg_node['ntype'], '__name__') else str(reg_node['ntype'])
            method = reg_node.get('function_name', 'N/A')
            print(f"  [{label}] {node_name} (type: {node_type}, method: {method})")
        print()
        
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
                    print(f"  {origin} --> {target}")
                else:
                    print(f"  {origin} (no connections)")
        
        print(f"\n{'='*60}\n")


    @property
    def communicate(self):
        return self._communicate
    
    @communicate.setter
    def communicate(self, communicate):
        if communicate is None:
            self._communicate = COMMUNICATE.DIRECT

        self._communicate = communicate(
                graphics=self.graphics.graphics,
                interface=self._register_interface,
                queue=self.queue or Queue()
        )


    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def execute(self, **data):
        
        forward = getattr(self, 'forward', None)

        try:
            exec = self.executor.execute(forward=forward)
            return exec(**data)

        except Exception as e:
            raise TypeError(f"Workflow execution failed: {e}")



    def forward(self, 
                name=None, 
                **data):

        print("Executing function in Workflow forward method")
        print(f"Function name: {name}")

        with self.communicate as comm:

            comm.send(data)

            for _label,_node in comm.generator():

                print(f"Executing Node: {_label}")
                
                transform = self._register_nodes.get(
                    _label, {}).get('transformer', None)
                
                if transform:
                    try:
                        _node.apply_transformer(transformer=transform)
                    except Exception as e:
                        print(f"Error applying transformer: {e}")
                
                _node.execute()

            received_msg = comm.receive()
            print(f"Received Message: {received_msg}")

        return received_msg





















