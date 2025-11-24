import os
import sys
import subprocess

from packages.dependencies import DependenciesMixin


class CondaManager(DependenciesMixin):

    __env_name__ = 'conda'
    
    def __init__(self, env_name=None, **kwargs):
        super().__init__(**kwargs)
        self.env_name = env_name


    def install_dependencies(self, package):
        cmd = ['conda', 'install', package, '-y']
        if self.env_name:
            cmd.extend(['-n', self.env_name])
        subprocess.run(cmd)
        print(f'✓ Installed {package} via conda')

    def uninstall_dependencies(self, package):
        cmd = ['conda', 'remove', package, '-y']
        if self.env_name:
            cmd.extend(['-n', self.env_name])
        subprocess.run(cmd)
        print(f'✓ Uninstalled {package} via conda')








