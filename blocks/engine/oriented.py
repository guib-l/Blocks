
from blocks.engine.graphic import (Graphics,
                                   graph_node,
                                   graph_cond,
                                   graph_loop)




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

        self.next_node = None
        self.prev_node = None

        self._graphics = []

    @property
    def graphics(self):
        return self._graphics


    def build(self, is_dag=False):

        self._graphics = []
        self.visited = set()
        self.progress = {
            node:0 for node in self.nodes.keys()
        }

        self.graphics.append(self.first)
        self.visited.add(self.first)

        for to in self.nodes[self.first].TO:
            self.queue.append(to)

        while self.queue:


            if self.allow_cycles:
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


            self._graphics.append(current)
            self.visited.add(current)


            for to in self.nodes[current].TO:    
                if to not in self.visited and to not in self.queue:
                    self.queue.append(to)

            if self.last is not None and current == self.last:
                break
        
        self.next_node = self._graphics[1]
        self.prev_node = []

        

    def __iter__(self):

        self.build()
        self.queue = []
        self.visited = set()

        for node in self._graphics:
            if self.progress[node] == 0:
                self.queue.append(node)

        return self
    
    def __next__(self):
        if not self.queue:
            raise StopIteration

        self.prev_node = self.next_node
        node = self.queue.pop(0)
        self.next_node = self.queue[0] if self.queue else []


        if node in self.visited:
            if not self.queue:
                raise StopIteration
            return self.__next__()

        self.visited.add(node)
        
        return self.nodes[node]





class CyclicGraphic(Graphics):

    def __init__(
            self, 
            links=None, 
            first=None, 
            last=None, 
            allow_cycles=True,
            max_nodes=999):
        
        super().__init__(links, first, last, allow_cycles)


        self.progress = {}
        self.queue = []
        self.visited = set()

        self.prev_queue = []

        self.graphics = []
        self.num_condition = 0
        self.num_loop = 0

        self.max_nodes = max_nodes


    def add_condition(
            self,
            start=None,
            default=None,
            arrival=None,
            ctype='IF', 
            method=None,
            switch=None,
            name=None,):
        
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
                    'type':graph_cond,
                    'args':{
                         'DEFAULT':default,
                         'method':method,
                         'switch':switch
                        }
                    },
            }
        )
        self.set_nodes()

    def add_loop(
            self,
            start=None,
            end=None,
            epoch=1,
            ctype='FOR',
            method=None,
            switch=None,
            name=None,):
        
        self.num_loop += 1
        if name is None:
            name = f"{ctype}-{self.num_loop:04d}"

        back = [dst for src,dst in self.links if src==end[-1]]

        for st in start:
            self.add_link(name,st)
        for ed in end:
            self.add_link(ed,name)


        self.nodes_type.update(
            {
                name:{
                    'type':graph_loop,
                    'args':{
                        'RETURN':back,
                        'epoch':epoch,
                        'method':method,
                        'switch':switch
                    }
                },
            }
        )
        self.set_nodes()



    def build(self):

        self.graphics = []
        self.visited = set()
        self.progress = {
            node:0 for node in self.nodes.keys()
        }

        self.graphics.append(self.first)
        self.visited.add(self.first)

        for to in self.nodes[self.first].TO:
            self.queue.append(to)

        while self.queue:

            idx = 0
            current = self.queue.pop(idx)

            if current in self.visited:
                if not self.allow_cycles:
                    raise Exception(f"Cycle detected at node {current}")


            self.graphics.append(current)
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

        self.number_iter = 0

        self.queue.append(self.first)

        return self
    
    def __next__(self):
        
        if self.prev_node is not None:
            prev_node_obj = self.nodes[self.prev_node]
            
            if hasattr(prev_node_obj, 'DEFAULT'):
                
                if isinstance(prev_node_obj.TO, list):
                    next_nodes = prev_node_obj.TO
                else:
                    next_nodes = [prev_node_obj.TO] \
                        if prev_node_obj.TO else [prev_node_obj.DEFAULT]
            else:
                next_nodes = prev_node_obj.TO \
                    if isinstance(prev_node_obj.TO, list) else [prev_node_obj.TO]
            
            for next_node in next_nodes:
                if next_node not in self.visited and next_node not in self.queue:
                    self.queue.append(next_node)
        
        if not self.queue:
            raise StopIteration
        
        node = self.queue.pop(0)

        if not self.allow_cycles:
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
        
        if self.number_iter == self.max_nodes:
            print(f"Infinite loop. Stopping iteration.")
            raise StopIteration

        self.number_iter += 1
        
        return self.nodes[node]



        




