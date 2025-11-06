import os
import sys
import subprocess

from . import DependenciesManager


class PipManager(DependenciesManager):
    def __init__(self, env_path=None):
        super().__init__(env_path)

    def install(self, package):
        cmd = [sys.executable, '-m', 'pip', 'install', package]
        if self.env_path:
            cmd.extend(['--target', self.env_path])
        subprocess.run(cmd)
        print(f'✓ Installed {package} via pip')

    def uninstall(self, package):
        cmd = [sys.executable, '-m', 'pip', 'uninstall', package, '-y']
        if self.env_path:
            cmd.extend(['--target', self.env_path])
        subprocess.run(cmd)
        print(f'✓ Uninstalled {package} via pip')





