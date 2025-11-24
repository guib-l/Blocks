import os,sys
import time
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *


from packages.package import Packages

from packages.package import SimpleProfile


cmds = [
    ['python3','--version'],
    ['pip','list']
]

# Test d'execution de profile
prf = SimpleProfile()
out = prf.execute(commands=cmds)




if __name__ == "__main__":

    pkg = Packages(
        directory = '.',
        env_name = 'pip-env.01',
        env_type = 'venv',
        mng_type = 'pip',
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
    #pkg.install_dependencies( dependencies=["scipy"],)
    #pkg.uninstall_dependencies( dependencies=["scipy"])

    # Sort de l'environement
    pkg.deactivate()

    pkg.move_env(
        target="myblock/"
    )
    pkg_copy = pkg.copy(
        new_name="pip-env.02",
        directory=".",
    )

    #pkg_copy.install_dependencies(
    #    dependencies=['matplotlib']
    #)
    
    if pkg == pkg_copy:
        print(" > Same objects")
    else:
        print(" > Different objects")


    pkg.merge(
        pkg = pkg_copy,
        directory = ".",
        ignore_dependencies = None,
    )

    pkg.uninstall_dependencies('numpy')

    print(" > Cleanup environments")
    print(pkg.dependencies)

    data = pkg.to_dict()
    print('DATA from pkg object : \n',data)

    X = Packages.from_dict(data)
    
    X.build()
    print(X)

    pkg.uninstall()
    pkg_copy.uninstall()


    sys.exit()




