import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *

from blocks.nodes.node import Node
from blocks.nodes.workflow import Workflow

from blocks.interface._interface import (MessageType,MESSAGE,Interface)

from blocks.project import Project




if __name__ == "__main__":

    node_1 = Node.load()
    node_2 = Node.load()
    node_3 = Node.load()
    node_4 = Node.load()

    project = Project(
        name    = "MyFirstProject",
        version = '0.0.1',
        path    = ".",
    )


    project.add_node([node_1,node_2,node_3])

    project.add_edge(node_1,node_2)

    project.add_edges([(node_2,node_3),
                       (node_1,node_3)])

    print(' > First node : ',project.starting_node)
    print(' > Last node  : ',project.ending_node)



    # Notes  à idées et dev future : 

    # V Correction du bug de Node | Interface
    # o Remplir le module Project et Workflow
    # o Gestion des logs et de l'historique
    # o Update des versions du projet (valable pour WF)
    # o Transformation en simple WF
    # o Exécution asynchrone / différé (v. WF. at Executor)
    # o Exécution dans un autre context 
    #           (passage par une gate ssh, sur serveur, etc)
    # o Accès documenation globale
    # o Passage en ligne de commande de tout ce qui se rapporte 
    #           au projet globale
    # o Choisir sur l'interface | l'executor sont globaux ou
    #           particulier fonction des node (choix possible)
    # o COMMUNICATOR dans chaque WF pour échanger et se déplacer 
    #           dans le labyrinthe de nodes
    #           Dois etre suffisament versatile pour admettre 
    #           un socket ou une gestion des fichiers
    # o Environnement par défaut ainsi que Executor par défauts




    # -----------------------
    # Start a first run of project

    project.feed_input(data  = {'test_value':0.00,
                                'test_argument':None},
                       mtype = MessageType.DIRECT)

    project.run()

    outp = project.fill_output()
    print("Output : \n",outp)


    # -----------------------
    # Re-start from specific node to an another

    project.add_node(node_4)
    project.add_edge(node_3,node_4)

    def transform(**data):
        return data["test_value"] + 42 
    
    project.handler_transformer(node_4, transform)

    project.feed_input(data  = {'test_value':0.00,
                                'test_argument':None},
                       mtype = MessageType.DIRECT)

    project.run(start_from = 2,
                end_at = 4,)

    outp = project.fill_output()
    print("Output : \n",outp)








