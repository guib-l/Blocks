import os
import sys
import json

import subprocess

from packages.dependencies import DependenciesMixin


class PipManager(DependenciesMixin):

    __mng_name__ = 'pip'
    
    def __init__(self, 
                 env_path=None, 
                 profile=None,
                 packages=None,):
        
        self.env_path = env_path
        self.profile = profile
        self.dependencies = packages or []

        if self.dependencies:
            self.install_dependencies(self.dependencies)


    def copy(self, **kwargs):
        return type(self)(
            env_path=self.env_path,
            profile=self.profile,
            dependencies=self.dependencies,
            **kwargs
        )
    

    # ============================================
    # Serialization of PipManager object

    """def to_dict(self):
        return {
            'env_path': self.env_path,
            'profile': self.profile,
            'packages': self.dependencies,
        }"""
    
    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            env_path=kwargs.get('env_path'),
            profile=kwargs.get('profile'),
            packages=kwargs.get('dependencies', []),
        )    

    def to_json(self,):
        return json.dumps(self.to_dict(),
                          indent=4)




    # ============================================
    # Methods of PIP utils

    def _exec_pip(self, command):
        try:
            if self.profile is None:
                subprocess.run(command, check=True)
            else:
                self.profile.execute(commands=command)
        except Exception as e:
            print(f"Error executing pip command {' '.join(command)}: {e}")
            return False
        return True

    def install_dependencies(self, package):
        
        if isinstance(package, list):
            for pkg in package:
                self.install_dependencies(pkg)
            return True
        
        if package in self.dependencies:
            return True
        
        self.dependencies.append(package)
        
        cmd = [sys.executable, '-m', 'pip', 'install', package]
        if self.env_path:
            cmd.extend(['--target', self.env_path])
        
        return self._exec_pip(cmd)

    def uninstall_dependencies(self, package):


        if isinstance(package, list):
            for pkg in package:
                self.uninstall_dependencies(pkg)
            return True
        
        print(package,self.dependencies)
        if package not in self.dependencies:
            return True
        
        self.dependencies.remove(package)

        cmd = [sys.executable, '-m', 'pip', 'uninstall', package, '-y']
        if self.env_path:
            cmd.extend(['--target', self.env_path])

        return self._exec_pip(cmd)

    def update_dependencies(self, package):
        cmd = [sys.executable, '-m', 'pip', 'install', '--upgrade', package]
        if self.env_path:
            cmd.extend(['--target', self.env_path])

        return self._exec_pip(cmd)

    def list_dependencies(self):
        cmd = [sys.executable, '-m', 'pip', 'list']
        if self.env_path:
            cmd.extend(['--target', self.env_path])

        try:
            if self.profile is None:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            else:
                result = self.profile.execute(cmd, capture_output=True, text=True)
            output = result.stdout
            packages = []
            for line in output.splitlines()[2:]:  # Skip header lines
                parts = line.split()
                if len(parts) >= 2:
                    packages.append((parts[0], parts[1]))
            return packages
        except Exception as e:
            print(f"Error listing dependencies via pip: {e}")
            return []
        












