import os,sys
from typing import *

import json
from tools.encoder import EnvJSONEncoder
from queue import Queue

import blocks.nodes.node as Node

from blocks.base import prototype 
from blocks.base.prototype import INSTALLER

from blocks.engine import ENVIRONMENT_TYPE
from blocks.nodes.graphics import AcyclicGraphMixin 

from blocks.interface.queue import QUEUE
from blocks.interface.interface import INTERFACE
from blocks.interface.communication import COMMUNICATE

from blocks.base.prototype import export_metadata



Workflow = TypeVar('Workflow', bound='Workflow')







def Install(object,
            name=None,
            directory=None,
            installer=INSTALLER.WORKFLOW):

    if directory:
        object.directory = directory
    if name:
        object.name = name

    
    object = object.__install__(name=object.name,
                       install_directory=object.directory,
                       installer=installer,)

    export_metadata(
        object,
        filename=object.__ntype__,
        format='json',
        directory=object.directory
    )


class REGISTER_NODE:

    _registrerd_types = {
            'prototype':Node.Node,
            'node':Node.Node,
            'workflow':Workflow,
        }

    def __init__(self, 
                 node, 
                 ntype='prototype',
                 function_name=None,
                 directory=None,
                 transformer=None):
        
        self.node          = node
        self.ntype         = ntype
        self.function_name = function_name
        self.directory     = directory
        self.transformer   = transformer # Une fonction de transformation des données avant exécution

    def __call__(self, key=None):
        if key is None:
            return {
                'node': self.node,
                'ntype': self.ntype,
                'directory': self.directory,
                'function_name': self.function_name,
                'transformer': self.transformer,
            }
        

    def to_dict(self,):
        return {
            'node': self.node.name,
            'ntype': self.ntype,
            'directory': self.directory,
            'function_name': self.function_name,
            'transformer': self.transformer,
        }

    @classmethod
    def from_dict(cls, **data):
        return cls(
            node=data.get('node', None),
            ntype=data.get('ntype', 'prototype'),
            directory=data.get('directory', None),
            function_name=data.get('function_name', None),
            transformer=data.get('transformer', None),
        )

    @classmethod
    def import_node(cls, **info):
        
        if isinstance(info.get('node', None), str):
            ntype = cls._registrerd_types[info.get('ntype','prototype')]
            node = ntype.load(
                name=info['node'],
                directory=info.get('directory', None),
                ntype='prototype'
            )
            print('NODE --->',node)
            return cls(
                node=node,
                function_name=info.get('function_name', None),
                directory=info.get('directory', None),
                transformer=info.get('transformer', None)
            )
        else:
            return cls(
                node=info['node'],
                function_name=info.get('function_name', None),
                directory=info.get('directory', None),
                transformer=info.get('transformer', None)
            )





class Workflow(prototype.Prototype):

    __ntype__ = "workflow"

    def __new__(cls, **kwargs):
        print('Creating Workflow subclass instance...')

        graphics    = kwargs.pop('graphics', AcyclicGraphMixin)

        cls = type(
            cls.__name__,
            (graphics,cls),
            {}
        )
        return super().__new__(cls, **kwargs)

    def __init__(self,
                 graphics=AcyclicGraphMixin, 
                 links:List[Tuple[Any,Any]] = [],
                 first:Any = None,
                 last:Any = None,
                 communicate:Any = COMMUNICATE.DIRECT,
                 interface:Any = INTERFACE.SIMPLE,
                 queue:Any = Queue(),
                 registered_nodes:Dict[str,Dict] = {},
                 **kwargs):

        super().__init__(**kwargs)

        self.__init_graph__(links=links, 
                            first=first, 
                            last=last)
        
        self.interface = INTERFACE.get(interface)
        self._queue = QUEUE.get(queue)

        self._registred_interface = []
        self._registred_nodes: Dict[str,Dict] = {}
        self._registred_nodes = self._sub_register_nodes(registered_nodes)

        self.communicate = COMMUNICATE.get(communicate)

    def _sub_register_nodes(self, nodes):

        for label, node in nodes.items():
            print(label,node) 

            value = REGISTER_NODE.import_node(**node)
            
            self._registred_nodes[label] = value()
            _node = self._registred_nodes[label]['node']

            self._registred_interface.append(
                        (label, self.interface(_node) ))

        return self._registred_nodes

#    def _sub_register_nodes(self, nodes):
#
#        def iregister_nodes(label, node_dict):
#            if isinstance(node_dict,dict):
#
#                if isinstance(node_dict['node'], str):
#                    self.import_node(node=node_dict.pop('node'),
#                                     label=label,
#                                     **node_dict )
#                    
#                elif isinstance(node_dict['node'], Node.Node):
#                    self._registred_interface.append(
#                        (label, 
#                         self.interface(node_dict['node']) ))
#                    
#                    self._registred_nodes[label] = node_dict
#
#                else:
#                    raise TypeError(
#                        f"Invalid node type for label {label}")
#        
#        for label, node in nodes.items():
#            print(label,node) 
#            iregister_nodes(label, node)
#
#        return self._registred_nodes
#
#
#
#    def import_node(self, node, label=None, **kwargs):
#        
#        if isinstance(node, str):
#            print(f"Loading node from name: {node} in: {self.directory}")
#            node = Node.Node.load(name=node,
#                                  directory=kwargs.get('directory',self.directory),
#                                  ntype=kwargs.get('ntype', 'prototype'))
#            print(f"Node loaded: {node}")
#
#        self._registred_interface.append((label or node.name, 
#                                          self.interface(node) ))
#        
#        self._registred_nodes[label or node.name] = {
#            'node': node,
#            'name':node.name,
#            'function_name':kwargs.get('function_name', None),
#            'transformer':kwargs.get('transformer', None)
#        }

    @property
    def communicate(self):
        return self._communicate
    
    @communicate.setter
    def communicate(self, communicate):
        if communicate is None:
            self._communicate = COMMUNICATE.DIRECT

        self._communicate = communicate(
                graphics=self.graphics,
                interface=self._registred_interface,
                queue=self._queue or Queue()
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
                
                transform = self._registred_nodes.get(
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



    def to_dict(self):
        def register_transform(func):
            import inspect
            return inspect.getsource(func).strip()

        _original = super().to_dict()
        _dict = {
            'graphics': self.graph_to_dict(),
            'registered_nodes':{
                label: {
                    'node': node_info['node'].name,
#                    'name':node_info['name'] or None,
                    'function_name': node_info['function_name'],
                    'transformer': "registrerd",
                }
                for label, node_info in self._registred_nodes.items()
            }
        }
        _original.update( _dict )
        return _original
    
    @classmethod
    def from_dict(cls, **data: dict):

        graphics_data = data.pop('graphics', {})

        print(graphics_data)

        registered_nodes_data = data.pop('registered_nodes', {})
        executor_data = data.pop('executor', {})
        environ_data = data.pop('environment', {})

        instance = cls(
            graphics=AcyclicGraphMixin,
            communicate='LABEL',
            interface='SIMPLE',
            queue='DATAQUEUE',
            registered_nodes=registered_nodes_data,
            **graphics_data,
            **data
        )
        print()
        return instance


    def to_json(self, 
                encoder=EnvJSONEncoder, 
                indent=4, **kwargs):

        return json.dumps(self.to_dict(), 
                          indent=indent, 
                          cls=encoder, **kwargs)






