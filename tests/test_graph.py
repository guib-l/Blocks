from configs import *


class  GRAPH_NODE:

    def __init__(
            self, 
            NAME="node-graph-00", 
            FROM=None, 
            TO=None):
        
        self.NAME  = NAME
        self.FROM  = FROM
        self.TO    = TO

    def __repr__(self):
        return f" {self.FROM} -> ({self.NAME}) -> {self.TO} "

    def resolve(self, **data):
        ...

class GRAPH_COND(GRAPH_NODE):

    def __init__(
            self, 
            NAME="node-graph-00", 
            FROM=None, 
            TO=None, 
            DEFAULT=None,
            method=None,
            switch=None,
            **kwargs):
        
        super().__init__(NAME, FROM, TO)
        self.DEFAULT = DEFAULT
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

    
class GRAPH_LOOP(GRAPH_NODE):

    def __init__(
            self, 
            NAME="node-graph-00", 
            FROM=None, 
            TO=None):
        
        super().__init__(NAME, FROM, TO)

    def resolved(self, **data):
        ...



class Graphics:
    def __init__(
            self,
            links=None,
            first=None,
            last=None,
            allow_cycles=False):
        
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
    
    def add_link(self, src, dst, node=True):
        
        self.links.append((src,dst))
        self.nodes_type.update(
            {
                src:{
                    'type':GRAPH_NODE,
                     'args':{}},
                dst:{
                    'type':GRAPH_NODE,
                     'args':{}}
            }
        )

        if node:
            self.set_nodes()

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

    def del_node(self, node):
        if node in self.nodes:
            del self.nodes[node]
            del self.nodes_type[node]
            self.del_links(
                [(src,dst) for src,dst in self.links \
                    if src==node or dst==node]
            )



class AcyclicGraphic(Graphics):
    def __init__(
            self,
            links=None,
            first=None,
            last=None):
        
        super().__init__(
            links=links, 
            first=first, 
            last=last, 
            allow_cycles=False)
        
        self.progress = {}
        self.queue = []
        self.visited = set()

        self.graphic = []




    def build(self, is_dag=False):

        self.graphic = []
        self.visited = set()
        self.progress = {
            node:0 for node in self.nodes.keys()
        }

        self.graphic.append(self.first)
        self.visited.add(self.first)

        for to in self.nodes[self.first].TO:
            self.queue.append(to)

        while self.queue:


            if is_dag:
                idx = 0
                status = True

                # On s'assure que tout les élement de current ont 
                # bien été déjà visités (idx == 0 par défaut)
                while status:
                    temp = self.queue[idx]
                    for elm in self.nodes[temp].FROM:
                        if elm not in self.visited:
                            idx += 1
                            status = True
                            break
                        else:
                            status = False
            else:
                idx = 0

            current = self.queue.pop(idx)

            if current in self.visited:
                if not self.allow_cycles:
                    raise Exception(f"Cycle detected at node {current}")


            self.graphic.append(current)
            self.visited.add(current)


            for to in self.nodes[current].TO:    
                if to not in self.visited and to not in self.queue:
                    self.queue.append(to)

            if self.last is not None and current == self.last:
                break

        

    def __iter__(self):

        self.build()
        self.queue = []
        self.visited = set()

        for node in self.graphic:
            if self.progress[node] == 0:
                self.queue.append(node)

        return self
    
    def __next__(self):
        if not self.queue:
            raise StopIteration

        node = self.queue.pop(0)

        if node in self.visited:
            if not self.queue:
                raise StopIteration
            return self.__next__()

        self.visited.add(node)
        
        return node



class CyclicGraphic(Graphics):

    def __init__(
            self, 
            links=None, 
            first=None, 
            last=None, 
            allow_cycles=True):
        
        super().__init__(links, first, last, allow_cycles)


        self.progress = {}
        self.queue = []
        self.visited = set()

        self.prev_queue = []

        self.graphic = []
        self.num_condition = 0


    def add_condition(
            self,
            start=None,
            default=None,
            arrival=None,
            ctype='IF', 
            method=None,
            switch=None,
            name=None,):
        import time
        self.num_condition += 1
        
        if name is None:
            name = f"{ctype}-{self.num_condition:04d}"
        
        
        for st in start:
            self.add_link(st,name)

        for ar in arrival:
            self.add_link(name,ar)

        self.nodes_type.update(
            {
                name:{
                    'type':GRAPH_COND,
                    'args':{
                         'DEFAULT':default,
                         'method':method,
                         'switch':switch
                        }
                    },
            }
        )
        self.set_nodes()



    def build(self):

        self.graphic = []
        self.visited = set()
        self.progress = {
            node:0 for node in self.nodes.keys()
        }

        self.graphic.append(self.first)
        self.visited.add(self.first)

        for to in self.nodes[self.first].TO:
            self.queue.append(to)

        while self.queue:

            idx = 0
            current = self.queue.pop(idx)

            if current in self.visited:
                if not self.allow_cycles:
                    raise Exception(f"Cycle detected at node {current}")


            self.graphic.append(current)
            self.visited.add(current)

            if hasattr(self.nodes[current], 'DEFAULT'):
                to = self.nodes[current].DEFAULT
                if to not in self.visited and to not in self.queue:
                    self.queue.append(to)
            else:        
                for to in self.nodes[current].TO:
                    if to not in self.visited and to not in self.queue:
                        self.queue.append(to)

            if self.last is not None and current == self.last:
                break

    def __iter__(self):

        self.build()
        self.queue = []
        self.visited = set()
        self.prev_node = None

        self.queue.append(self.first)

        return self
    
    def __next__(self):
        
        if self.prev_node is not None:
            prev_node_obj = self.nodes[self.prev_node]
            
            if hasattr(prev_node_obj, 'DEFAULT'):
                
                if isinstance(prev_node_obj.TO, list):
                    next_nodes = prev_node_obj.TO
                else:
                    next_nodes = [prev_node_obj.TO] if prev_node_obj.TO else [prev_node_obj.DEFAULT]
            else:
                next_nodes = prev_node_obj.TO if isinstance(prev_node_obj.TO, list) else [prev_node_obj.TO]
            
            for next_node in next_nodes:
                if next_node not in self.visited and next_node not in self.queue:
                    self.queue.append(next_node)
        
        if not self.queue:
            raise StopIteration
        
        node = self.queue.pop(0)

        if node in self.visited:
            if not self.queue:
                print('No more nodes to visit. Stopping iteration.')
                raise StopIteration
            return self.__next__()

        self.visited.add(node)
        self.prev_node = node  
        
        if self.last is not None and node == self.last:
            print(f"Reached last node {self.last}. Stopping iteration.")
            raise StopIteration
        
        return self.nodes[node]



        

if __name__ == "__main__":
    


    # ==============================================

    link = [ ('g',2),(4,1),(0,'g'),
            (2,4),(2,54),(3,4),(7,54),
            ('g',3),(54,8),(3,8) ]

    graph = AcyclicGraphic(
        links=link, 
        first=0, 
        last=None)
    
    print(graph.links)
    print(graph.nodes)

    graph.build()

    print(graph.graphic)

    for g in graph:
        
        print(g)

    print(': Finished ---')
    # ==============================================


    link = [ ('g',2),(4,1),(0,'g'),
            (2,4),(2,54),(3,4),
            ('g',3),(54,8),(3,8), 
            (96,88) ]

    graph = CyclicGraphic(
        links=link, 
        first=0, 
        last=None)
    
    print(graph.nodes)

    def eq(key_attr='n', value='n'):
        if key_attr==value:
            return False
        return True
    
    graph.add_condition(
        start=[8],
        default=96,
        arrival=[45,96],
        ctype='IF',
        method=eq,
        switch={
            45:True,
            96:False
        }    
    )

    print(graph.links)
    print(graph.nodes)

    graph.build()

    print(graph.graphic)

    print(graph.nodes_type)

    for g in graph:

        print('Node : ',g.NAME)
        g.resolve()
    








