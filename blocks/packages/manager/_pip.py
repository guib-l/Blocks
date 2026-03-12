import os
import sys
import json

import subprocess

from blocks.packages.dependencies import DependenciesMixin

from blocks.utils.logger import *

class PipManager(DependenciesMixin):

    __mng_name__ = 'pip'
    
    def __init__(self, 
                 env_path=None, 
                 profile=None,
                 dependencies=None,
                 executable=None):
        
        self.env_path = env_path
        self.profile = profile
        self.dependencies = dependencies or []

        python_bin = f"python{sys.version_info.major}.{sys.version_info.minor}"
        if env_path:
            bin_dir = os.path.abspath(os.path.join(env_path, 'bin'))
            candidates = [python_bin, f"python{sys.version_info.major}", "python"]
            self.executable = next(
                (os.path.join(bin_dir, c) for c in candidates
                 if os.path.isfile(os.path.join(bin_dir, c))),
                sys.executable,
            )
        else:
            self.executable = sys.executable

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

    def to_dict(self):
        return {
            'env_path': self.env_path,
            'profile': self.profile,
            'packages': self.dependencies,
        }
    
    @classmethod
    def from_dict(cls, **kwargs):
        return cls(
            env_path=kwargs.get('env_path'),
            profile=kwargs.get('profile'),
            dependencies=kwargs.get('dependencies', []),
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
            env_logger.error(f"Error executing pip command {' '.join(command)}: {e}")
            return False
        return True
    
    def _is_installed(self, package):
        """Return True only if the package is installed inside this venv."""
        cmd = [self.executable, '-m', 'pip', 'show', package]
        try:
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.returncode != 0:
                return False
            
            for line in result.stdout.splitlines():
                if line.startswith('Location:'):
                    location = line.split(':', 1)[1].strip()
                    env_path = os.path.abspath(self.env_path) if self.env_path else None
                    return env_path is not None and location.startswith(env_path)
            return False
        except Exception:
            return False

    def install_depends(self, package):

        if self._is_installed(package):
            env_logger.info(f"Package '{package}' is already installed.")
            return True

        cmd = [self.executable, '-m', 'pip', 'install', package]        
        return self._exec_pip(cmd)


    def install_dependencies(self, package):
        
        if isinstance(package, list):
            for pkg in package:
                self.install_depends(pkg)
            return True        
        return self.install_depends(package)
    
    def uninstall_depends(self, package):

        cmd = [self.executable, '-m', 'pip', 'uninstall', package, '-y']        
        return self._exec_pip(cmd)

    def uninstall_dependencies(self, package):

        if isinstance(package, list):
            for pkg in package:
                self.uninstall_depends(pkg)
            return True
        
        if package in self.dependencies:
            self.dependencies.remove(package)

        return self.uninstall_depends(package)
    

    def update_dependencies(self, package):
        cmd = [self.executable, '-m', 'pip', 'install', '--upgrade', package]
        return self._exec_pip(cmd)

    def list_dependencies(self):
        cmd = [self.executable, '-m', 'pip', 'list']

        try:
            if self.profile is None:
                result = subprocess.run(cmd, check=True, capture_output=True, text=True)
            else:
                result = self.profile.execute(cmd, capture_output=True, text=True)
                
            output = result.stdout if self.profile is None else result['outputs'][0]
        
            packages = []
        
            for line in output.splitlines()[2:]:  
                parts = line.split()
                if len(parts) >= 2:
                    packages.append((parts[0], parts[1]))
            return packages
        
        except Exception as e:
            env_logger.error(f"Error listing dependencies via pip: {e}")
            return []
        












