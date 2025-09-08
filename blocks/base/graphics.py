#!/usr/bin/env python3
import os
import sys
import math
import copy


class TopologicError(Exception):
    """Exception pour des erreur topologique"""
    pass

class GraphicsError(Exception):
    """Exception pour des erreur lié à l'objet TopologicalGraph"""
    pass


class TopologicGraphics:

    def __init__(self, links=None, first=None, last=None):
        """
        Initialize the TopologicalSorter with an optional list of links
        Args:
            links (list of tuples): List of directed edges (src, dst)
        """
        self.forward  = {}
        self.backward = {}

        self.queue    = []
        self.link     = []

        self.progress = {}
        self.nodes    = set()
        self.visited  = set()

        self._graphics = None

        self.first = first
        self.last  = last

        if links:
            self.add_links(links)

    def copy(self):
        """
        Create a shallow copy of the TopologicalSorter instance
        Returns:
            TopologicalSorter: A new instance with the same properties
        """
        new_sorter = TopologicGraphics(links=self.link, 
                                       first=self.first, 
                                       last=self.last)
        new_sorter.forward = copy.deepcopy(self.forward)
        new_sorter.backward = copy.deepcopy(self.backward)
        return new_sorter

    def to_dict(self):
        """
        Convert the graph to a dictionary representation
        Returns:
            dict: Dictionary representation of the graph
        """
        return {
            'nodes': list(self.nodes),
            'links': self.link,
            'first': self.first,
            'last' : self.last,
        }

    def write_graphics(self, format='txt'):
        """
        Return content of graphics in specified format
        """
        content = None

        if format=='txt':
            return content
        else:
            raise GraphicsError("Format of content not reconized")

    def read_graphics(self, data):
        pass
        

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
        self._graphics = list(iter(self))
        return self._graphics
    
    @property
    def first(self):
        """
        Get the first node to start the topological sort
        Returns:
            int: The first node to start the sort
        """
        return self._first
    
    @first.setter
    def first(self, first):
        """
        Set the first node to start the topological sort
        Args:
            first (int): The first node to start the sort
        """
        self._first = first

    
    @property
    def last(self):
        """
        Get the last node to end the topological sort
        Returns:
            int: The last node to end the sort
        """
        return self._last
    
    @last.setter
    def last(self, last):
        """
        Set the last node to end the topological sort
        Args:
            last (int): The last node to end the sort
        """
        self._last = last

    def is_visited(self, node):
        """
        Check if a node has already been visited
        Args:
            node (int): The node to check
        Returns:
            bool: True if the node has been visited, False otherwise
        """
        if node in self.visited:
            return True
        return False
    
    def linked_to(self, node, dtype="resume"):
        """
        Get the nodes linked to a given node in the graph
        Args:
            node (int): The node to check
            dtype (str): The type of links to return ('forward', 'backward', 'resume')
        Returns:
            list: List of nodes linked to the given node
        """
        if dtype=='forward':
            return self.forward[node]
        if dtype=='backward':
            return self.backward[node]
        if dtype=='resume' or dtype==None:
            return {
                'next':self.forward[node],
                'from':self.backward[node],
            }

    def linked(self, node):
        """
        Get the nodes that are required to execute a given node
        Args:
            node (int): The node to check
        Returns:
            list: List of nodes that are required to execute the given node
        """
        try:
            value = self.linked_to(node, dtype='forward')
        except:
            value = []
        return value
        
    def required(self, node):
        """
        Get the nodes that are required to execute a given node
        Args:
            node (int): The node to check
        Returns:
            list: List of nodes that are required to execute the given node
        """
        try:
            value = self.linked_to(node, dtype='backward')
        except:
            value = []
        return value


    def add_link(self, src, dst):
        """
        Add a single link (edge) to the graph
        Args:
            src (int): Source node
            dst (int): Destination node
        """
        self.nodes.add(src)
        self.nodes.add(dst)

        self.link.append((src,dst))

        if src not in self.forward:
            self.forward[src] = []
        self.forward[src].append(dst)

        if dst not in self.backward:
            self.backward[dst] = []
        self.backward[dst].append(src)

    def del_link(self, src, dst):
        """
        Remove a single link (edge) from the graph
        Args:
            src (int): Source node
            dst (int): Destination node
        """
        self.link = [l for l in self.link if l[0]!=src and l[1]!=dst ]
        self.forward[src] = [l for l in self.forward[src] if l!=dst ]
        self.backward[dst] = [l for l in self.backward[dst] if l!=src ]

        if self.forward[src]==[]:
            del self.forward[src]
            self.nodes.remove(src)
            
        if self.backward[dst]==[]:
            del self.backward[dst]

    def del_links(self, links):
        """
        Remove a list of link (edge) from the graph
        Args:
            links (list): List of tuple of links
        """

        for values in links:
            self.del_link(*values)

    def add_links(self, links):
        """
        Add a list of link (edge) to the graph
        Args:
            links (list): List of tuple of links
        """
        for values in links:
            self.add_link(*values)

    def add_node(self, node):
        """
        Add a node to the graph
        Args:
            node (int): The node to add
        """
        if node not in self.nodes:
            self.nodes.add(node)
            self.forward[node]  = []
            self.backward[node] = []
            self.link.append((node,node))

    def del_node(self, node):
        """
        Remove a node from the graph and its associated links
        Args:
            node (int): The node to remove
        """
         
        if node in self.nodes:
            src,dst = node,node

            for elm in self.nodes:
                
                if elm in self.forward.keys():
                    self.forward[elm] = [l for l in self.forward[elm] if l!=dst ]
                    if self.forward[elm]==[]:
                        del self.forward[elm]
                                
                if elm in self.backward.keys():
                    self.backward[elm] = [l for l in self.backward[elm] if l!=src ]
                    if self.backward[elm]==[]:
                        del self.backward[elm]
                    
            if self.backward[src]:
                del self.backward[src]
                    
            if self.forward[src]:
                del self.forward[src]

            self.nodes.remove(node)
            self.link = [l for l in self.link if l[0]!=src and l[1]!=dst ]
             

    def build(self,):
        """
        Build the topological sort by initializing the progress dictionary
        and setting the first node to start the sort
        """
        self.progress = {}

        for link in self.link:
            src,dst = link
            
            if src not in self.progress:
                self.progress[src] = 0
            if dst not in self.progress:
                self.progress[dst] = 0
            
            self.progress[dst] += 1

            if self.progress[src]==0:
                local_first = src 
        
        if self.first and local_first!=self.first:
            self.progress[local_first]  = 1
            self.progress[self.first]   = 0

    def __iter__(self,):
        """
        Initialize the iterator state
        Returns:
            self: The TopologicalSorter instance
        """          
        self.queue   = []
        self.visited = set()
        
        for node in self.nodes:
            if node not in self.nodes:
                raise StopIteration
            if self.progress[node] == 0:
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
        
        #if self.last in self.visited:
        #    raise StopIteration
        
        node = self.queue.pop(0)
        self.visited.add(node)

        if node in self.forward:
            for neighbor in self.forward[node]:
                self.progress[neighbor] -= 1
                if self.progress[neighbor] == 0:
                    self.queue.append(neighbor)
                    
        return node




