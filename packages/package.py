import os
import sys

from typing import List, Optional
from pathlib import Path

from dataclasses import dataclass

from contextlib import ExitStack
import subprocess



@dataclass
class SimpleProfile:

    commands: List[List[str]] = None
    directory: str = "./"
    shell: bool = False
    timeout: Optional[int] = None

    def __post_init__(self):
        self.directory = Path(self.directory)
        if not self.directory.exists():
            raise ValueError(f"Directory {self.directory} does not exist")

    def _execute_command(self, cmd: List[str]) -> tuple[str, str, int]:
        """Execute a single command and return stdout, stderr, and return code."""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                shell=self.shell,
                #bufsize=1,
                cwd=str(self.directory)
            )
            stdout, stderr = process.communicate(timeout=self.timeout)
            return stdout, stderr, process.returncode
        
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"Command {cmd} timed out after {self.timeout} seconds")
        
        except Exception as e:
            raise RuntimeError(f"Failed to execute command {cmd}: {e}")

    def execute(self, commands=None) -> dict:
        """Execute all commands and return results."""
        
        if commands is None:
            commands = self.commands
        
        if isinstance(commands, list) and all(isinstance(c, str) for c in commands):
            commands = [commands,]

        results = {
            'outputs': [],
            'errors': [],
            'return_codes': [],
            'success': True
        }

        for i, cmd in enumerate(commands):
            try:
                stdout, stderr, returncode = self._execute_command(cmd)
                results['outputs'].append(stdout)
                results['errors'].append(stderr)
                results['return_codes'].append(returncode)
                
                if returncode != 0:
                    results['success'] = False
                    
            except Exception as e:
                results['outputs'].append("")
                results['errors'].append(str(e))
                results['return_codes'].append(-1)
                results['success'] = False

        return results



class Select:

    __slots__ = ("_environ","_manager")

    def __init__(self, 
                 env_type: str, 
                 mng_type: str):
        self.environ = env_type
        self.manager = mng_type
    
    def to_dict(self):
        return {
            "env": self._environ.__class__,
            "mng": self._manager.__class__,
        }
    
    @property
    def environ(self):
        return self._environ
    
    @environ.setter
    def environ(self, env_type):
        if env_type is None:
            raise ValueError('An environment type must be provided')
        if env_type == 'conda':
            from packages.environ._conda import CondaEnv
            env_type = CondaEnv
        elif env_type == 'venv':
            from packages.environ._venv import VenvEnv
            env_type = VenvEnv
        else:
            if not hasattr(env_type,'__envtype__') and env_type.__envtype__ != 'EnvironMixin' :
                raise ValueError('The environment must be a PackageEnvironment instance or a valid string identifier')

        self._environ = env_type
    @property
    def manager(self):
        return self._manager

    @manager.setter
    def manager(self, manager):

        if manager is None:
            raise ValueError('A package manager must be provided')
        
        if manager == 'pip':
            from packages.manager._pip import PipManager
            manager = PipManager
        elif manager == 'conda':
            from packages.manager._conda import CondaManager
            manager = CondaManager
        else:
            if not hasattr(manager,'__envtype__') and manager.__envtype__ != 'DependenciesMixin' :
                raise ValueError('The manager must be a PackageManager instance or a valid string identifier')
            
        self._manager = manager



class Packages(Select):

    __slots__ = ("directory","dependencies","env_name",
                 "auto_build","profile","_backend_manager",
                 "_backend_environ")

    def __init__(self,
                 directory = '.',
                 env_name = 'conda-env.01',
                 env = 'conda',
                 mng = 'conda',
                 dependencies = ['numpy'],
                 auto_build = False,
                 profile = None,
                 **args ):
        
        self.directory = Path(directory)
        self.env_name = env_name

        super().__init__(env_type=env, 
                         mng_type=mng)

        self.dependencies = dependencies
        self.auto_build = auto_build
        
        self.profile = profile or SimpleProfile()

        if auto_build:
            self.build(**args)
        
    @classmethod
    def from_dict(cls, **data: dict):
        return cls(**data)
    
    def to_dict(self):
        return {
            "directory": str(self.directory),
            "env_name": self.env_name,
            "dependencies": self.dependencies,
            "auto_build": self.auto_build,
            "env": self._environ.to_dict(),
            "mng": self._manager.to_dict(),          
        }


    def build(self, **kwargs):
        print(f"Building environment {self.env_name} with dependencies {self.dependencies}")

        self._backend_environ = self.environ(
            name = self.env_name,
            directory = self.directory,
        )

        self._backend_manager = self.manager(
            #context = self._backend_environ,
            packages = self.dependencies,
            env_path=self._backend_environ.env_path,
            profile=self.profile,
        )

    def install(self):
        print(f"Installing dependencies in environment {self.env_name}")
        self._backend_environ.install_context()

    def uninstall(self):
        print(f"Uninstalling dependencies from environment {self.env_name}")
        self._backend_environ.uninstall_context()

    def activate(self):
        print(f"Activating environment {self.env_name}")
        self._backend_environ.enable()

    def update(self, dependencies: List[str]=None):
        print(f"Updating dependencies {dependencies} in environment {self.env_name}")
        for dep in dependencies:
            self._backend_manager.update_dependencies(dep)

    def list_dependencies(self):
        print(f"Listing dependencies for environment {self.env_name}")
        return self._backend_manager.list_context()
    
    def install_dependencies(self, dependencies: List[str]):
        print(f"Installing dependencies {dependencies} in environment {self.env_name}")
        self._backend_manager.install_dependencies(dependencies)

    def uninstall_dependencies(self, dependencies: List[str]):
        print(f"Uninstalling dependencies {dependencies} from environment {self.env_name}")
        self._backend_manager.uninstall_dependencies(dependencies)

    def deactivate(self):
        print(f"Deactivating environment {self.env_name}")
        self._backend_environ.disable()

    def move_env(self, target: str):
        print(f"Moving environment {self.env_name} to {target}")
        self._backend_environ.move_env(
            target_dir=target,
            delete_source=True,
        )
        self.directory = self._backend_environ.directory
        print(f"New environment path: {self.directory}")
        self._backend_manager.env_path = self._backend_environ.env_path

    def copy(self, 
             new_name: Optional[str] = None, 
             directory: Optional[str] = None,):
        print(f"Copying environment {self.env_name}")

        assert new_name is not None, "A new name must be provided for the copied environment"

        return type(self)(
            directory = directory or str(self.directory),
            env_name = new_name,
            dependencies = self.dependencies.copy(),
            auto_build = True,
            profile = self.profile,
            env = self._backend_environ.__class__,
            mng = self._backend_manager.__class__,
        )

    def add_dependencies(self, dependency: str):
        print(f"Adding dependency {dependency} to environment {self.env_name}")

    def del_dependencies(self, dependency: str):
        print(f"Deleting dependency {dependency} from environment {self.env_name}")

    # TODO : implement diff logic
    def diff(self, other_pkg):
        print(f"Comparing environment {self.env_name} with another environment")
        return {}

    # TODO : implement merge logic
    def merge(self, 
              pkg, 
              directory: str, 
              ignore_dependencies: Optional[List[str]] = None):
        print(f"Merging environment {self.env_name} with another environment into directory {directory}")


    def __eq__(self, other):
        if not isinstance(other, Packages):
            return False
        if len(self.dependencies) != len(other.dependencies):
            return False
        for dep in self.dependencies:
            if dep not in other.dependencies:
                return False
        return True           

    def __str__(self):
        return f"Packages(env_name={self.env_name}, \
env={self._backend_environ}, mng={self._backend_manager}, dependencies={self.dependencies})"

    def __repr__(self):
        return self.__str__()
    


