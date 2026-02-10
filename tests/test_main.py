import os,sys
import time
from configs import *

from blocks.blocks import Blocks



if __name__ == "__main__":
      
    # ===============================================
    # Récupération et exécution dans son environnement
    print("\n"+"*"*40)

    txt = f"""
# Initialisation  en ligne de comande d'un projet complet (Workflow), et entré 
# dans le scope de ce nœud:

$ blocks <name> -<option> <location> 

> option  
    l : loads existing project
    n : new project at <location>

# Creation d'un nouveau projet : construction en ligne de commande de la base
# de travail (type, installer, environement, etc) -> gestionnaire de création


# Récupération d'un objet maitre (Workflow ou dérivé)


# Regarder ce qu'il y a dans le pool de ce worflow

$ blocks list


# Action sur les objets du pool (ajouter/retirer/mettre à jour dess nœuds)

$ blocks remove <name>

$ blocks add <name> <location>


    """

    print(txt)

    main = Blocks()




