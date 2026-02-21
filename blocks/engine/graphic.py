import time

class  graph_node:

    def __init__(
            self, 
            NAME="node-graph-00", 
            FROM=None, 
            TO=None):
        """Initialize a graph node."""
        
        self.NAME = NAME 
        self.FROM = FROM 
        self.TO   = TO 

    def resolve(self, **data):
        ...

    def __repr__(self):
        return f" {self.FROM}>({self.NAME})>{self.TO} "


class graph_cond(graph_node):

    def __init__(
            self, 
            DEFAULT=None,
            method=None,
            switch=None,
            **kwargs):
        
        super().__init__(**kwargs)

        self.DEFAULT = DEFAULT #if isinstance(DEFAULT,list) else [DEFAULT]
        self.method = method
        self.switch = switch or {}

    def resolve(self, **data):
        
        try:
            if self.method is not None and self.switch is not None:
                results = self.method(**data)
                for key,item in self.switch.items():
                    if item==results:
                        self.TO = [key]
                        return

            self.TO = [ self.DEFAULT ]
        except Exception as e:
            self.TO = [ self.DEFAULT ]


class graph_loop(graph_node):

    def __init__(
            self, 
            RETURN=None,
            epoch=1,
            method=None,
            switch=None,
            **kwargs):
        
        super().__init__(**kwargs)

        self.RETURN = RETURN
        self.epoch = epoch
        self.method = method
        self.switch = switch or {}

    def resolve(self, **data):

        self.epoch -= 1
        if self.epoch <= 0:
            self.TO = self.RETURN

    

class Graphics:

    def __init__(
            self,
            links=None,
            first=None,
            last=None,
            allow_cycles=False):
        """
        Initialize a graph.
        
        Args:
            links (list of tuples): List of edges in the graph, where each edge is represented as a tuple (src, dst).
            first (str): The starting node of the graph.
            last (str): The ending node of the graph.
            allow_cycles (bool): Whether to allow cycles in the graph.
        """
        
        self.links = []
        self.first = first
        self.last  = last

        self.nodes      = {}
        self.nodes_type = {}

        self.add_links(links)

        self.allow_cycles = allow_cycles

    @property
    def first(self):
        return self._first

    @first.setter
    def first(self, value):
        self._first = value

    @property
    def last(self):
        return self._last

    @last.setter
    def last(self, value):
        self._last = value

    # ========================= Link Manipulation Methods =========================
    # Methods to add/remove links, and to query the graph structure.


    def add_link(self, src, dst, node=True):
        
        self.links.append((src,dst))
        self.nodes_type.update(
            {
                src:{
                    'type':graph_node,
                     'args':{}},
                dst:{
                    'type':graph_node,
                     'args':{}}
            }
        )

        if node:
            self.set_nodes()

    def add_links(self, links):
        for link in links:
            self.add_link(link[0], link[1], node=False)

        self.set_nodes()
    
    def del_link(self, src, dst):
        if (src,dst) in self.links:
            self.links.remove((src,dst))
            self.set_nodes()

    def del_links(self, links):
        for link in links:
            self.del_link(link[0], link[1])

    def linked_to(self, node):
        return {
            'node': node,
            'prev': [src for src,dst in self.links if dst==node],
            'next': [dst for src,dst in self.links if src==node],
        }

    def required_nodes(self):
        return set(
            [src for src,_ in self.links] + 
            [dst for _,dst in self.links])

    # ========================= Node Manipulation Methods =========================
    # Methods to add/remove nodes, and to query the graph structure.

    def set_nodes(self):

        keys = set(
            [src for src,_ in self.links] + 
            [dst for _,dst in self.links])

        for node in keys:
            ARL = [src for src,dst in self.links \
                        if dst==node and src in keys]
            DST = [dst for src,dst in self.links \
                        if src==node and dst in keys]
            
            objt = self.nodes_type[node]['type']
            args = self.nodes_type[node]['args']

            self.nodes.update(
                {
                    node:objt(
                        NAME=node,
                        FROM=ARL,
                        TO=DST,
                        **args)
                }
            )

    def del_node(self, node):
        if node in self.nodes:
            del self.nodes[node]
            del self.nodes_type[node]
            self.del_links(
                [(src,dst) for src,dst in self.links \
                    if src==node or dst==node]
            )










