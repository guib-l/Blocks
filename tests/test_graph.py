import time

from configs import *


    

from blocks.engine.graphic import (Graphics,
                                   graph_node,
                                   graph_cond,
                                   graph_loop)


from blocks.engine.oriented import AcyclicGraphic, CyclicGraphic


if __name__ == "__main__":

    # ==============================================
    print("="*40)

    link = [ ('g',2),(4,1),(0,'g'),
            (2,4),(2,54),(3,4),(7,54),
            ('g',3),(54,8),(3,8) ]

    graph = Graphics(
        links=link, 
        first=0, 
        last=None)
    
    print("Nodes : ")
    for n in graph.nodes:
        print('   ',graph.nodes[n])  


    # ==============================================
    print("="*40)

    link = [ ('g',2),(4,1),(0,'g'),
            (2,4),(2,54),(3,4),(7,54),
            ('g',3),(54,8),(3,8) ]

    graph = AcyclicGraphic(
        links=link, 
        first=0, 
        last=None)
    
    print("Nodes : ")
    for n in graph.nodes:
        print('   ',graph.nodes[n])

    graph.build()

    print('Graphics : \n',graph.graphics)


    print('> Iterating through the graph nodes : ')
    for g in graph:
        
        print('Node : ',g)
        

    print('> Finished iterating through the graph nodes.')

    # ==============================================
    print("="*40)

    link = [ ('g',2),(4,1),(0,'g'),
            (2,4),(2,54),(3,4),
            ('g',3),(54,8),(3,8), 
            (96,52) ]

    graph = CyclicGraphic(
        links=link, 
        first=0, 
        last=None)
    
    print("Nodes : ")
    for n in graph.nodes:
        print('   ',graph.nodes[n])

    def eq(key_attr='n', value='n'):
        if key_attr==value:
            return False
        return True
    
    graph.add_condition(
        start=[8],
        default=96,
        end=[45,96],
        ctype='IF',
        method=eq,
        switch={
            45:True,
            96:False
        }    
    )

    graph.build()

    print('Graphics : \n',graph.graphics)
    
    print('> Iterating through the graph nodes : ')
    for g in graph:

        print('Node : ',g.NAME)
        g.resolve()
    
    print('> Finished iterating through the graph nodes.')


    # ==============================================
    print("="*40)


    link = [ ('g',2),(4,1),(0,'g'),
            (2,4),(2,54),(3,4),
            ('g',3),(54,8),(3,8), 
            (96,52),(8,47),(47,9) ]

    graph = CyclicGraphic(
        links=link, 
        first=0, 
        last=None,
        allow_cycles=True)
    

    graph.add_loop(
        start=[2],
        end=[8],
        epoch=3,
        ctype='FOR',
    )
    
    print("Nodes : ")
    for n in graph.nodes:
        print('   ',graph.nodes[n])

    
    print('> Iterating through the graph nodes : ')
    for g in graph:

        print('Node : ',g.NAME)
        g.resolve()
    
    print('> Finished iterating through the graph nodes.')



















