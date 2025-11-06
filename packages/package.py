import os
import sys

from typing import List, Optional
from pathlib import Path



class Profile:
    def execute(self, command: str):
        print(f"Executing command in profile: {command}")




class Select:

    def __init__(self, env_type: str, mng_type: str):
        self.environ = env_type
        self.manager = mng_type

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
            #if not isinstance(env_type,PackageEnvironment):
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
            #if not isinstance(manager,PackageManager):
            raise ValueError('The manager must be a PackageManager instance or a valid string identifier')
            
        self._manager = manager



class Packages(Select):

    def __init__(self,
                 directory = '.',
                 env_name = 'conda-env.01',
                 env = 'conda',
                 mng = 'conda',
                 dependencies = ['numpy'],
                 auto_build = False,
                 profile = None,
                 use_shell = True, ):
        
        self.directory = Path(directory)
        self.env_name = env_name

        super().__init__(env_type=env, mng_type=mng)

        self.dependencies = dependencies
        self.auto_build = auto_build
        self.profile = profile
        self.use_shell = use_shell

    def build(self):
        print(f"Building environment {self.env_name} with dependencies {self.dependencies}")

    def activate(self):
        print(f"Activating environment {self.env_name}")

    def update(self, dependencies: List[str]):
        pass

    def deactivate(self):
        print(f"Deactivating environment {self.env_name}")

    def move_env(self, target: str):
        print(f"Moving environment {self.env_name} to {target}")

    def copy(self):
        print(f"Copying environment {self.env_name}")
        
    def add_dependencies(self, dependency: str):
        print(f"Adding dependency {dependency} to environment {self.env_name}")

    def del_dependencies(self, dependency: str):
        print(f"Deleting dependency {dependency} from environment {self.env_name}")

    def diff(self, other_pkg):
        print(f"Comparing environment {self.env_name} with another environment")
        return {}

    def merge(self, pkg, directory: str, ignore_dependencies: Optional[List[str]] = None):
        print(f"Merging environment {self.env_name} with another environment into directory {directory}")

    def __eq__(self, other):
        pass

    def __ne__(self, other):
        pass

    def __str__(self):
        return f"Packages(env_name={self.env_name}, env={self.env}, mng={self.mng}, dependencies={self.dependencies})"

    def __repr__(self):
        return self.__str__()
    
    def to_dict(self):
        return {
            "directory": str(self.directory),
            "env_name": self.env_name,
            "dependencies": self.dependencies,
            "auto_build": self.auto_build,
            "profile": self.profile,
            "use_shell": self.use_shell,
        }
    
    def from_dict(self, data: dict):
        self.directory = Path(data.get("directory", '.'))
        self.env_name = data.get("env_name", 'conda-env.01')
        self.dependencies = data.get("dependencies", ['numpy'])
        self.auto_build = data.get("auto_build", False)
        self.profile = data.get("profile", None)
        self.use_shell = data.get("use_shell", True)

    def copy(self):
        return type(self)(
            directory = str(self.directory),
            env_name = self.env_name,
            dependencies = self.dependencies,
            auto_build = self.auto_build,
            profile = self.profile,
            use_shell = self.use_shell,
            env = self.environ.__name__.lower(),
            mng = self.manager.__name__.lower(),
        )



