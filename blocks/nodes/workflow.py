import os,sys
from typing import *

import blocks.nodes.node as Node

from blocks.base import prototype 
from blocks.base.prototype import INSTALLER
from blocks.nodes.graphics import AcyclicGraphMixin 


Workflow = TypeVar('Workflow', bound='Workflow')



def export_metadata(block: prototype.Prototype, 
                    filename: str,
                    format: str = 'json',
                    directory: str = None, ) -> None:
    """
    Export metadata from a Block instance to a file.
    Args:
        block (Block): The Block instance to export metadata from.
        filename (str): The name of the file to export to (without extension).
        format (str): The format to export the metadata in ('json', 'csv', etc.).
    """
    if os.path.splitext(filename)[1] != '':
        if os.path.splitext(filename)[1] != f".{format}":
            raise ValueError("Le nom de fichier doit se terminer par " \
"l'extension correspondant au format spécifié.")    
        
    content = None
    if format == 'json':
        content = block.to_json()
    elif format == 'csv':
        content = block.to_csv()
    else:
        raise ValueError(f"Unsupported format: {format}")
    
    if content:
        path = os.path.join(directory or block.directory,
                            block.name,
                            f"{filename}.{format}")

        with open(path, "w") as f:
            f.write(content)


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
                 first_node:Any = None,
                 last_node:Any = None,
                 nodes:Dict[str,Node.Node] = {},
                 **kwargs):

        super().__init__(**kwargs)

        self.__init_graph__(links=links, 
                            first=first_node, 
                            last=last_node)
        
        self._registred_nodes = {}

        for label, node in nodes.items():
            if isinstance(node, Node.Node):
                self.import_node(node, label=label)
            elif isinstance(node, dict):
                self.import_node(label=label,**node)
            else:
                raise TypeError("Node must be an instance of Node or a dict.")
        

    # -----------------------------------------------------
    # Logique du noeud à exécuter
        
    def execute(self, **data):
        
        forward = getattr(self, 'forward', None)

        try:
            exec = self.executor.execute(forward=forward)
            return exec(**data)

        except Exception as e:
            raise TypeError(f"Workflow execution failed: {e}")

    def forward(self, name=None, **data):

        print("Executing function in Workflow forward method")
        print(f"Function name: {name}")

        for item in self.graphics:

            print(f"Processing node: {item}")
            node_info = self._registred_nodes.get(item)

            if node_info:
                node = node_info['node']
                output = node.execute(**data)
                print(f"Node '{item}' output: {output}")
            else:
                print(f"Node '{item}' not found in registered nodes.")

        return None


    def import_node(self, node,
                    label=None,
                    **kwargs):
        
        self._registred_nodes[label or node.name] = {
            'node': node,
            'name':node.name,
            'function_name':None,
            **kwargs
        }

