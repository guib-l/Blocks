import os
import sys
import subprocess

from . import DependenciesManager


class CondaManager(DependenciesManager):
    def __init__(self, env_name=None):
        super().__init__()
        self.env_name = env_name

    
    def install_context(self,):
        raise NotImplementedError
    def uninstall_context(self,):
        raise NotImplementedError
    def move_context(self,):
        raise NotImplementedError

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