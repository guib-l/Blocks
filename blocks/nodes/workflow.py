from typing import *

from blocks.base.signal import Signal
from blocks.interface._interface import MESSAGE,MessageType
import blocks.nodes.node as node

from blocks.nodes.graphics import TopologicGraphics 


Workflow = TypeVar('Workflow', bound='Workflow')






class Workflow(node.Node):

    __ntype__ = "workflow"

    def __init__(self, 
                 graphics = None,
                 communicator = None,
                 global_environment=True,
                 global_executor=True,
                 **kwargs):
        
        super().__init__(**kwargs)

        if isinstance(graphics, TopologicGraphics):
            self._graphics = graphics
        elif isinstance(graphics, dict):
            self._graphics = TopologicGraphics.from_dict(**graphics)
        else:
            if self._mandatory_attr: raise NotImplementedError('Graphics not informed')
            else: self._graphics = TopologicGraphics()
    
        self._graphics.build()

        self.currents_nodes = {}

        self.communicator       = communicator

        self.global_environment = global_environment
        self.global_executor    = global_executor



    # -----------------------------------------------------
    # Execute methods
    
    def forward(self, **data):

        if self.communicator is None:

            for node_index in self._graphics.graphics:
                node = self.currents_nodes[node_index]
                data = node.execute(**data)
            
            output = data
            return output
    

    # -----------------------------------------------------
    # Graphics methods

    def graph_to_dict(self,):
        graph = self._graphics.to_dict()
        graph.update({'nodes':None})
        return graph

    @property
    def graphics(self,):
        return self._graphics.graphics
    
    @graphics.setter
    def graphics(self, value):
        if isinstance(value, TopologicGraphics):
            self._graphics = value
        elif isinstance(value, dict):
            self._graphics = TopologicGraphics.from_dict(**value)
        else:
            raise TypeError("Value not 'TopologicGraphics' or 'dict'")

    @property
    def node(self,idx):
        return self._graphics.nodes[idx]
    
    @property
    def nodes(self,):
        return self._graphics.nodes
    
    @property
    def links(self,):
        return self._graphics.link

    @property
    def starting_node(self,):
        return self._graphics.first

    @starting_node.setter
    def starting_node(self, start):
        self._graphics.first = start

    @property
    def ending_node(self,):
        return self._graphics.last

    @ending_node.setter
    def ending_node(self, end):
        self._graphics.last = end

    # -----------------------------------------------------
    # Nodes methods

    def add_node(self, node, index=None):
        if index is None:
            index = len(self.currents_nodes) + 1
            while True:
                if index not in self.currents_nodes.keys():
                    break
                index += 1
        if index not in self.currents_nodes.keys():
            self.currents_nodes.update({index:node})
        else:
            raise ValueError("Index exist in currend nodes")
        
    def add_nodes(self,):
        ...

    def remove_node(self, index: int):
        if index in self.currents_nodes.keys():
            del self.currents_nodes[index]
        else:
            raise ValueError("Index didn't exist in currend nodes")

    def remove_nodes(self,):
        ...
        



    def connect_nodes(self, from_node: str, to_node: str = None):
        
        if isinstance(from_node,int):
            if from_node not in self.currents_nodes.keys():
                raise ValueError("Node unknow in 'from_node'")
            
            if to_node not in self.currents_nodes.keys():
                raise ValueError("Node unknow in 'to_node'")
            
            self._graphics.add_link(from_node,to_node)
        else:
            try:
                self._graphics.add_links(from_node)
            except:
                raise TypeError("'from_node' not <int> or <iterable>")

    def disconnect_nodes(self, from_node: str, to_node: str = None):
        
        if isinstance(from_node,int):
            if from_node not in self.currents_nodes.keys():
                raise ValueError("Node unknow in 'from_node'")
            
            if to_node not in self.currents_nodes.keys():
                raise ValueError("Node unknow in 'to_node'")
            
            self._graphics.del_link(from_node,to_node)
        else:
            try:
                self._graphics.del_links(from_node)
            except:
                raise TypeError("'from_node' not <int> or <iterable>")
        

    

    def handler_transformer(self,):
        ...
    def handler_message(self,):
        ...


    def to_dict(self,):
        ...
    def to_json(self,):
        ...
    def from_dict(self,):
        ...






    def __str__(self,):
        return super().__str__()
    
    def __len__(self,):
        return len(self.currents_nodes)
    
    def __getstate__(self):
        return super().__getstate__()
    
    def __setstate__(self, state):
        return super().__setstate__(state)
    
    def __contains__(self, key):
        return super().__contains__(key)
    
    def __copy__(self):
        return super().__copy__()
    
    def __deepcopy__(self, memo):
        return super().__deepcopy__(memo)
    
    def __sizeof__(self):
        return super().__sizeof__()



    