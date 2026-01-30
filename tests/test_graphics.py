from configs import *

from blocks.nodes.graphics import AcyclicGraph




if __name__ == "__main__":
    

    link = [(0,1),(1,2),(1,11),
            (1,4),(2,4),(4,5),
            (5,6),(6,7),(6,8),
            (8,9),(9,10)]
    print("> Link : \n",link)


    # Perform topological sort on the links
    graph = AcyclicGraph(links=link, first=1, last=8)
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











