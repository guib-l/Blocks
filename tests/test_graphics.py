from configs import *

from blocks.nodes.graphics import AcyclicGraph


class _graphical_node:

    def __init__(
            self, 
            name, 
            FROM=None, 
            TO=None):
        
        self.name  = name
        self.FROM  = FROM
        self.TO    = TO

    def resolved(self, **kwargs):
        pass

    def __repr__(self):
        return f" {self.FROM} -> ({self.name}) -> {self.TO} "


class _graphical_condition(_graphical_node):

    def __init__(
            self, 
            name, 
            FROM=None, 
            TO=None,
            DEFAULT=None,
            ctype='IF',
            method=None,
            switch={}):
        
        super().__init__(name, FROM, TO)
        self.DEFAULT = DEFAULT

        self.ctype  = ctype
        self.method = method
        self.switch = switch


    def resolved(self, **data):
        
        try:
            results = self.method(**data)
            for key,item in self.switch.items():
                if item==results:
                    self.TO = key
                    break
        except:
            self.TO = self.DEFAULT



class TopologicError(Exception):
    """Exception pour des erreur topologique"""
    pass

class GraphicsError(Exception):
    """Exception pour des erreur lié à l'objet TopologicalGraph"""
    pass



class GraphicsBase:

    __ntype__ = 'graphics'

    def __init__(
            self, 
            links=None, 
            nodes=None, 
            first=None,
            last=None,
            graph_node=_graphical_node ):
        
        self.nodes_keys = nodes if nodes is not None else set()
        self.links = links if links is not None else []
        self.first = first
        self.last  = last

        self._nodes = {}

        self.graph_node = graph_node
        self._graphics = []

        self.queue     = []
        self.visited   = []
        self.progress  = 0

    # ********************

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

    @property
    def links(self):
        return self._links
    
    @links.setter
    def links(self, value):
        self._links = value
        for link in self._links:
            self._nodes_keys.update(link)


    @property
    def nodes_keys(self):
        return self._nodes

    @nodes_keys.setter
    def nodes_keys(self, value):
        self._nodes_keys = value

#    @property
#    def nodes(self):
#        return self._nodes



    @property
    def graphics(self):
        """
        Perform topological sort on the provided links (compatibility method)
        Args:
            links (list of tuples): List of directed edges (src, dst)
        Returns:
            list: List of nodes in topological order
        """
        self.build()
        return self._graphics
    
    
    # ********************

    def is_cycle(self,):

        visited    = set()
        notvisited = set()

        for node in self._graphics:
            
            for _from in node.FROM:
                if _from not in visited:
                    notvisited.add(_from)
                
            if node in notvisited:
                return True
            
            visited.add(node.name)
        return False


    def __iter__(self,):
        """
        Initialize the iterator state
        Returns:
            self: The TopologicalSorter instance
        """          
        self.queue   = []
        self.visited = set()
        
        for node in self.nodes:
            if node not in self.nodes: # ??
                raise StopIteration
            self.queue.append(node)

        print('queue : ',self.queue)
        return self

    def __next__(self,):
        """
        Return the next node in topological order

        Raises:
            StopIteration: If there are no more nodes to visit
        Returns:
            int: The next node in topological order
        """        
        if not self.queue:
            raise StopIteration
                
        node = self.queue.pop(0)
        self.visited.add(node)


        _node = self._graphics[self.progress]
        self.progress += 1
        return _node



    # ********************

    def build(self):

        self.nodes = set()        
        visited    = set()
        queue      = [self.first]
        iterator   = []

        while queue:
            current = queue.pop(0)
            
            if current in visited:
                continue
            
            visited.add(current)
            iterator.append(current)

            if self.last is not None and current == self.last:
                break
            
            next_nodes = [dst for src, dst in self.links if src == current]
            for node in next_nodes:
                queue.append(node)

        _graph =  {}
        
        for node in iterator:
            ARL = [src for src,dst in self.links \
                        if dst==node and src in iterator]
            DST = [dst for src,dst in self.links \
                        if src==node and dst in iterator]
            
            _graph.update( { 
                node: self.graph_node(
                    name=node,
                    FROM=ARL,
                    TO=DST,
                )}
            )
            self.nodes.add(node)

        self._graphics = [_graph[it] for it in iterator]


        if self.is_cycle():
            raise TopologicError('Cycle is not allowed in this graphic.')




        


class Graphics(GraphicsBase):

    def __init__(
            self, 
            links=None,
            max_nodes=100,
            **kwargs):
        
        self.max_nodes = max_nodes

        self.conditionnal_binding = {}
        self.num_condition = 0

        super().__init__(links, **kwargs)


    # ********************
    def build(self):

        self.nodes = set()        
        visited    = set()
        queue      = [self.first]
        iterator   = []

        print(self.links)

        while queue:
            current = queue.pop(0)
            
            if current in visited:
                continue
            
            visited.add(current)
            iterator.append(current)
            print("Current node : ",current)

            if self.last is not None and current == self.last:
                break
            
            next_nodes = [dst for src, dst in self.links if src == current]
            for node in next_nodes:
                queue.append(node)

            if len(iterator) > self.max_nodes:
                raise GraphicsError(f"Maximum number of nodes ({self.max_nodes}) exceeded in the graphic.")
        
        print("Iterator : ",iterator)
        _graph =  {}
        
        for node in iterator:
            ARL = [src for src,dst in self.links \
                        if dst==node and src in iterator]
            DST = [dst for src,dst in self.links \
                        if src==node and dst in iterator]

            if node in self.conditionnal_binding.keys():
                _graph.update( { 
                    node: self.conditionnal_binding[node]
                })

            else:
                _graph.update( { 
                    node: self.graph_node(
                        name=node,
                        FROM=ARL,
                        TO=DST,
                    )}
                )
            self.nodes.add(node)

        self._graphics = [_graph[it] for it in iterator]
        print("Graphics : ",self._graphics)

    def add_condition_link(
            self, 
            enter, 
            exit, 
            default, 
            ctype='IF', 
            method=None,
            switch=None,
            name=None):
        
        import time
        self.num_condition += 1
        
        if name is None:
            name = f"CONDITION-{ctype}-{self.num_condition:04d}"

        # Add the conditional link to the graph
        self.links.append((enter, name))
        for elm in exit:
            self.links.append((name, elm))

        ARL = [src for src,dst in self.links if dst==name]
        DST = [dst for src,dst in self.links if src==name]
        self.conditionnal_binding.update(
            {
                name:_graphical_condition(
                    name=name,
                    FROM=ARL,
                    TO=DST,
                    DEFAULT=default,
                    ctype=ctype, 
                    method=method,
                    switch=switch,
                )
            }
        )


        self.nodes.add(name)
        self.nodes.add(default)

        self.build()  # Rebuild the graph to include the new lin


    def __iter__(self,):
        """
        Initialize the iterator state
        Returns:
            self: The TopologicalSorter instance
        """          
        self.queue   = []
        self.visited = set()
        
        for node in self.nodes:
            if node not in self.nodes: # ??
                raise StopIteration
            self.queue.append(node)

        return self

    def __next__(self,):
        """
        Return the next node in topological order

        Raises:
            StopIteration: If there are no more nodes to visit
        Returns:
            int: The next node in topological order
        """        
        if not self.queue:
            raise StopIteration
                
        node = self.queue.pop(0)
        self.visited.add(node)

        print(node)


        _node = self._graphics[self.progress]
        self.progress += 1
        return _node







if __name__ == "__main__":
    



    link = [ ('g',2),(4,1),(0,'g'),(2,4),(2,54),(3,4),('g',3),(54,8)]

    graph = GraphicsBase(links=link, first=2, last=None)
    print(graph.links)

    graph.build()

    print(graph._graphics)


    for g in graph:
        print('***')
        print(g)


    print("****"*10)
    link = [ ('g',2),(4,1),(0,'g'),(2,4),(2,54),(3,4),('g',3),(54,8)]

    graph = Graphics(links=link, first=0, last=None)
    print(graph.links)

    graph.build()

    print(graph._graphics)

    def eq(key_attr='n', value='n'):
        if key_attr==value:
            return True
        return False

    graph.add_condition_link(
        enter=8,
        exit=('a',9),
        default=9,
        ctype='IF',
        method=eq,
        switch={
            'a':True,
            9:False
        }    
    )

    graph._links.append(('a',5))
    graph.build()

    print('+++++++++++++++++++++')

    print(graph.links)

    for g in graph:
        print(g)

        g.resolved()


    print(graph._graphics)



    sys.exit()














































    link = [(0,1),(1,2),(1,11),
            (1,4),(2,4),(4,5),
            (5,6),(6,7),(6,8),
            (8,9),(9,10)]
    print("> Link : \n",link)


    # Perform topological sort on the links
    graph = AcyclicGraph(
        links=link, first=1, last=8)
    print("> Graph : \n",graph)

    graph.del_link(0,1)

    order = graph.graphics  # Use the generator to get the sorted order
    print("Traversal order:", order)

    # Add a new link and regenerate the order
    graph.add_link(2, 12)
    graph.add_link(12, 11)

    graph.build()

    for _g in graph:
        print(" > Execute node : ",_g)

    print(graph.frontward)
    print(graph.backward)

    graph.del_node(5)

    print(graph.frontward)
    print(graph.backward)

    print(graph.link)

    graph.del_link(2,12)
    print(graph.graphics)
    print('Nodes : ',graph.nodes)
    
    order = graph.graphics 

    print("Traversal order with new link:", order)

    for _g in graph:
        print(" > Execute node : ",_g)


    print("Test of AcyclicGraph completed successfully.")
    print("="*40+"\n")





    link = [ (0,1),(1,2),(1,3),(2,4),(3,4),(4,5) ]

    graph = AcyclicGraph(links=link)
    print(graph.graphics)



    








