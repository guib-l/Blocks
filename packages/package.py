import os
import sys

from typing import List, Optional
from pathlib import Path

from dataclasses import dataclass

from contextlib import ExitStack
import subprocess


from tools.serializable import SerializableMixin

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

    def _execute_command(self, cmd: List[str], **kwargs) -> tuple[str, str, int]:
        """Execute a single command and return stdout, stderr, and return code."""
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=kwargs.pop('text', True),
                shell=self.shell,
                cwd=str(self.directory),
                **kwargs
            )
            stdout, stderr = process.communicate(timeout=self.timeout)
            return stdout, stderr, process.returncode
        
        except subprocess.TimeoutExpired:
            process.kill()
            raise RuntimeError(f"Command {cmd} timed out after {self.timeout} seconds")
        
        except Exception as e:
            raise RuntimeError(f"Failed to execute command {cmd}: {e}")

    def execute(self, commands=None, **kwargs) -> dict:
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
                stdout, stderr, returncode = self._execute_command(cmd, **kwargs)
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

    #__slots__ = ("_environ","_manager")

    def __init__(self, 
                 env_type: str, 
                 mng_type: str):
        
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
        elif hasattr(env_type,'__dict__'):
            pass
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
        elif hasattr(manager,'__dict__'):
            pass
        else:
            if not hasattr(manager,'__envtype__') and manager.__envtype__ != 'DependenciesMixin' :
                raise ValueError('The manager must be a PackageManager instance or a valid string identifier')
            
        self._manager = manager


class Packages(Select, SerializableMixin):

    __slots__ = ("directory","dependencies","env_name",
                 "auto_build","profile","_backend_manager",
                 "_backend_environ",'env_type','mng_type')

    def __init__(self,
                 directory = '.',
                 env_name = 'conda-env.01',
                 env_type = 'conda',
                 mng_type = 'conda',
                 dependencies = [],
                 auto_build = False,
                 profile = None,
                 **args ):

        self.directory = Path(directory)
        self.env_name = env_name

        self.env_type = env_type
        self.mng_type = mng_type

        super().__init__(env_type=env_type, 
                         mng_type=mng_type)

        self.dependencies = dependencies
        self.auto_build = auto_build
        
        self.profile = profile or SimpleProfile()

        if auto_build:
            self.build(**args)

    def package_to_dict(self):
        return {
            'env_name':self.env_name,
            'env_type': self.env_type.__name__ if hasattr(self.env_type,'__name__') else str(self.env_type),
            'mng_type': self.mng_type.__name__ if hasattr(self.mng_type,'__name__') else str(self.mng_type),
            'dependencies':self.dependencies,
            'directory': str(self.directory),
            'auto_build': self.auto_build,
            'profile': {
                'commands': self.profile.commands,
                'directory': str(self.profile.directory),
                'shell': self.profile.shell,
                'timeout': self.profile.timeout,
            } if self.profile else None,
        }


    # ============================================
    # Build of Packages object

    @property
    def _is_built(self) -> bool:
        """True if both backend_environ and backend_manager have been instantiated."""
        return (hasattr(self, '_backend_environ') and self._backend_environ is not None
                and hasattr(self, '_backend_manager') and self._backend_manager is not None)

    def build(self, **kwargs):
        print(f"Building environment {self.env_name} with dependencies {self.dependencies}")

        self._backend_environ = self.environ(
            name=self.env_name,
            directory=self.directory,
        )
        print(f"Environment {self.env_name} built successfully")

        self._backend_manager = self.manager(
            dependencies=self.dependencies,
            env_path=self._backend_environ.env_path,
            profile=self.profile,
        )
        print(f"Manager for environment {self.env_name} initialized successfully")

    def install(self):
        print(f"Installing dependencies in environment {self.env_name}")
        self._backend_environ.install_context()

    def uninstall(self):
        print(f"Uninstalling dependencies from environment {self.env_name}")
        self._backend_environ.uninstall_context()

    @property
    def site_packages(self) -> str:
        """Convenience proxy to the backend environment's site-packages path."""
        return self._backend_environ.site_packages

    def activate(self) -> bool:
        print(f"Activating environment {self.env_name}")
        return self._backend_environ.enable()

    def update(self, dependencies: List[str]=None):
        print(f"Updating dependencies {dependencies} in environment {self.env_name}")
        for dep in dependencies:
            self._backend_manager.update_dependencies(dep)

    def list_dependencies(self):
        print(f"Listing dependencies for environment {self.env_name}")
        return self._backend_manager.list_dependencies()
    
    def install_dependencies(self, dependencies: List[str]):
        print(f"Installing dependencies {dependencies} in environment {self.env_name}")
        self._backend_manager.install_dependencies(dependencies)

    def uninstall_dependencies(self, dependencies: List[str]):
        print(f"Uninstalling dependencies {dependencies} from environment {self.env_name}")
        self._backend_manager.uninstall_dependencies(dependencies)

    def deactivate(self) -> bool:
        print(f"Deactivating environment {self.env_name}")
        return self._backend_environ.disable()

    # ============================================
    # Context manager — activation / désactivation automatique

    def __enter__(self) -> 'Packages':
        """Activate the environment when entering a `with` block.

        If the environment has not been built yet, `build()` is called
        automatically so that a freshly constructed `Packages` object can be
        used directly as a context manager::

            with Packages(env_name='my-env', env_type='venv', mng_type='pip') as pkg:
                pkg.install_dependencies(['numpy'])
        """
        if not self._is_built:
            self.build()
        self.activate()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        """Deactivate the environment when leaving the `with` block.

        Exceptions raised inside the block are *not* suppressed.
        """
        self.deactivate()
        return False  # propagate any exception

    def __call__(self) -> 'Packages':
        """Allow a `Packages` instance to be used directly as a context manager
        factory when an explicit call style is preferred::

            pkg = Packages(env_name='my-env', env_type='venv', mng_type='pip')
            with pkg() as p:
                ...
        """
        return self

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
            env_type = self._backend_environ.__class__,
            mng_type = self._backend_manager.__class__,
        )

    def add_dependencies(self, dependency: str):
        print(f"Adding dependency {dependency} to environment {self.env_name}")

    def del_dependencies(self, dependency: str):
        print(f"Deleting dependency {dependency} from environment {self.env_name}")

    def diff(self, other_pkg: 'Packages') -> dict:
        """
        Compare the installed packages of two environments.

        Returns a dict with three keys:
            - 'only_in_self'  : list of (name, version) present only in this env
            - 'only_in_other' : list of (name, version) present only in other_pkg
            - 'common'        : list of (name, self_version, other_version) —
                                version differs when self_version != other_version
        """
        print(f"Comparing environment {self.env_name} with {other_pkg.env_name}")

        self_deps  = {name: ver for name, ver in self.list_dependencies()}
        other_deps = {name: ver for name, ver in other_pkg.list_dependencies()}

        self_names  = set(self_deps)
        other_names = set(other_deps)

        return {
            'only_in_self':  [(n, self_deps[n])  for n in sorted(self_names  - other_names)],
            'only_in_other': [(n, other_deps[n]) for n in sorted(other_names - self_names)],
            'common':        [(n, self_deps[n], other_deps[n])
                              for n in sorted(self_names & other_names)],
        }

    def merge(self,
              pkg: 'Packages',
              new_name: str,
              directory: Optional[str] = None,
              ignore_dependencies: Optional[List[str]] = None) -> 'Packages':
        """
        Merge this environment with *pkg* into a brand-new environment.

        The resulting environment contains the union of all installed packages
        from both environments, minus anything listed in *ignore_dependencies*.
        When the same package exists in both, the version from *pkg* takes
        precedence (it will be installed last, effectively upgrading).

        Args:
            pkg:                  The other Packages object to merge with.
            new_name:             Name of the merged environment.
            directory:            Target directory (defaults to self.directory).
            ignore_dependencies:  Package names to exclude from the merge.

        Returns:
            A new Packages object for the merged environment.
        """
        print(f"Merging {self.env_name} + {pkg.env_name} → {new_name}")

        if not isinstance(pkg, Packages):
            raise TypeError(f"Expected a Packages object to merge with, got {type(pkg)}")
        
        if pkg.env_type != self.env_type or pkg.mng_type != self.mng_type:
            raise ValueError("Both environments must have the same type and manager to be merged")

        ignore = set(ignore_dependencies or [])

        # Collect installed packages from both environments
        self_deps  = {name: ver for name, ver in self.list_dependencies()}
        other_deps = {name: ver for name, ver in pkg.list_dependencies()}

        # Union — other_pkg wins on version conflicts
        merged = {**self_deps, **other_deps}
        merged_names = [name for name in merged if name not in ignore]

        merged_pkg = type(self)(
            directory  = str(directory or self.directory),
            env_name   = new_name,
            env_type   = self.env_type,
            mng_type   = self.mng_type,
            dependencies = [],
            auto_build = False,
            profile    = self.profile,
        )
        merged_pkg.build()
        merged_pkg.install_dependencies(merged_names)
        merged_pkg.dependencies = merged_names

        print(f"Merged environment '{new_name}' created with {len(merged_names)} packages.")
        return merged_pkg


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
    


