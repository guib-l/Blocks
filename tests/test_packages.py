import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *


from packages.package import Packages





if __name__ == "__main__":

    pkg = Packages(
        directory = '.',
        env_name = 'conda-env.01',
        env = 'conda',
        mng = 'conda',
        dependencies = ['numpy'],
        auto_build = False,
        profile = None,
        use_shell = True,
    )

    # Construit l'environement et télécharges des dependences
    pkg.build()

    # Active l'environement
    pkg.activate()

    # Ajoute des dépendances dans l'environement
    pkg.update(
        dependencies=["scipy"],
    )

    # Sort de l'environement
    pkg.deactivate()

    pkg.move_env(
        target="myblocks/"
    )

    pkg_copy = pkg.copy()

    pkg_copy.add_dependencies('matplotlib')

    if pkg == pkg_copy:
        print("Same objects")

    diff = pkg.diff(pkg_copy)
    print('Differences : ',diff)

    pkg.merge(
        pkg = pkg_copy,
        directory = ".",
        ignore_dependencies = None,
    )

    pkg.del_dependencies('numpy')

    




    sys.exit()




