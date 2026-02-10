from configs import *

from blocks.nodes.graphics import AcyclicGraph


class _graphical_node:

    def __init__(
            self, 
            name, 
            FROM=None, 
            TO=None,
            VISIT=None):
        
        self.name  = name
        self.FROM  = FROM
        self.TO    = TO
        self.VISIT = VISIT

    def __repr__(self):
        return f" {self.FROM} -> ({self.name}) -> {self.TO} "


class GraphicsBase:

    __ntype__ = 'graphics'

    def __init__(
            self, 
            links=None, 
            nodes=None, 
            first=None,
            graph_node=_graphical_node ):
        
        self.nodes = nodes if nodes is not None else set()
        self.links = links if links is not None else []
        self.first = first

        self.graph_node = graph_node
        self._graphics = None


    # ********************

    @property
    def first(self):
        return self._first
    
    @first.setter
    def first(self, value):
        self._first = value

    @property
    def links(self):
        return self._links
    
    @links.setter
    def links(self, value):
        self._links = value
        for link in self._links:
            self._nodes.update(link)

    @property
    def nodes(self):
        return self._nodes

    @nodes.setter
    def nodes(self, value):
        self._nodes = value

    # ********************

    def build(self):
        self._graphics = [
            self.graph_node(
                name=self.first,
                FROM=[],
                TO=[dst for src,dst in self.links if src==self.first],
            )
        ]

        DST = [d for _,d in self.links]

        def get_index(node, table=None):
            idx = [i for i,t in enumerate(table) if t==node]
            return idx

        print(get_index(1,DST))

        progress = 0
        iter = 0

        while (progress<len(self._graphics)):

            node = self._graphics[progress]
            print('==================')
            
            print('NAME',node.name)
            print('TO',node.TO)

            for name in node.TO:
                print(name,[dst for src,dst in self.links if src==name])

                self._graphics.append(
                    self.graph_node(
                        name=name,
                        FROM=[src for src,dst in self.links if dst==name],
                        TO=[dst for src,dst in self.links if src==name],
                    )
                )

                progress += 1

            if len(node.TO)==0:
                print('END',progress,len(self._graphics))
                break

            if iter > 15:
                break
            
            iter+=1
        



#        for node in self.nodes:
#            _src = node
#            
#            self._graphics.append(
#                self.graph_node(
#                    name=_src,
#                    FROM=[src for src,dst in self.links if dst==_src],
#                    TO=[dst for src,dst in self.links if src==_src],
#                )
#            )



        print(self._graphics)
        


class Graphics(GraphicsBase):

    def __init__(self, links=None, nodes=None, first=None):
        super().__init__(links, nodes, first)


    def __iter__(self,):
        return self

    def __next__(self):
        return 





if __name__ == "__main__":
    



    link = [ ('g',2),(4,1),(0,'g'),(2,4),(2,54),(3,4),('g',3)]

    graph = GraphicsBase(links=link, first=0)
    print(graph.links)
    print(graph.nodes)

    graph.build()











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



    








