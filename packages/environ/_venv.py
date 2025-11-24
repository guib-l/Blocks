import os
import sys
import shutil
import subprocess

import venv
from packages.virtualenv import EnvironMixin


class VenvEnv(venv.EnvBuilder, EnvironMixin):
    """
    Creates and manages a specialized Python environment with specific dependencies
    and configuration for a particular use case.
    """
    context_exists: bool = False
    __env_name__ = 'venv'
    
    def __init__(self, 
                 name=None,
                 directory=None,
                 system_site_packages=False, 
                 clear=False, 
                 symlinks=False,
                 upgrade=False, 
                 with_pip=True, 
                 prompt=None, 
                 requirements=None,
                 auto_build=True):
        
        super().__init__(system_site_packages=system_site_packages, 
                         clear=clear,
                         symlinks=symlinks, 
                         upgrade=upgrade, 
                         with_pip=with_pip,
                         prompt=prompt,)
        self.env_name = name
        self.directory = directory
        self.env_path = os.path.join(directory, name) if directory and name else None
        self.requirements = requirements or []


        if self.env_path and os.path.exists(self.env_path):
            self.context_exists = True
            print(f"Virtual environment {self.env_name} already exists.")

        if auto_build and not self.context_exists:
            if self.install_context():
                print(f"Virtual environment {self.env_name} created successfully.")
            else:
                print(f"Failed to create virtual environment {self.env_name}.")

    def copy(self, 
             new_name: str = None,
             new_directory: str = None):
        
        return type(self)(
            name = new_name or self.env_name,
            directory = new_directory or os.path.dirname(self.env_path),
            system_site_packages = self.system_site_packages,
            clear = self.clear,
            symlinks = self.symlinks,
            upgrade = self.upgrade,
            with_pip = self.with_pip,
            prompt = self.prompt,
            requirements = self.requirements,
            auto_build = True,
        )

    def enable(self,):
        env_dir = self.env_path

        # Get activation paths
        bin_path = os.path.join(env_dir, 'bin')
        if not os.path.exists(bin_path):
            return False
        
        # Check if the environment is already activated
        if 'VIRTUAL_ENV' in os.environ and os.environ['VIRTUAL_ENV'] == env_dir:
            return True
        
        # Update sys.path to use the environment's packages
        site_packages = os.path.join(
            env_dir, 
            'lib', 
            f'python{sys.version_info.major}.{sys.version_info.minor}', 
            'site-packages'
        )
        if os.path.exists(site_packages) and site_packages not in sys.path:
            sys.path.insert(0, site_packages)

        # Get the old sys.prefix
        self.old_prefix = sys.prefix
        sys.prefix = env_dir
        
        # Add the bin directory to PATH
        os.environ['PATH'] = f"{bin_path}:{os.environ['PATH']}"
        
        # Set VIRTUAL_ENV environment variable
        os.environ['VIRTUAL_ENV'] = env_dir
        return True
        
    
    def disable(self,):
        if 'VIRTUAL_ENV' not in os.environ:
            return False
            
        # Clean up PATH to remove the bin directory
        bin_path = os.path.join(os.environ['VIRTUAL_ENV'], 'bin')
        os.environ['PATH'] = os.environ['PATH'].replace(f"{bin_path}:", "")
        
        # Unset VIRTUAL_ENV
        del os.environ['VIRTUAL_ENV']

        # Restore the original sys.prefix if we saved it
        if hasattr(self, 'old_prefix'):
            sys.prefix = self.old_prefix
            delattr(self, 'old_prefix')
        return True

    def get_context(self):
        return {
            "env_name": self.env_name,
            "env_path": self.env_path,
            "requirements": self.requirements
        }

    def diff(self, other):
        return False
    
    def merge(self, other):
        return False
    
    def install_context(self,):

        env_dir = self.env_path
        if not env_dir:
            return False
        
        print(f'Creating virtual environment at {env_dir}...')
            
        # Create the environment
        self.create(env_dir)
        return True

    def uninstall_context(self,):
        import shutil
        env_dir = self.env_path
        
        if not env_dir or not os.path.exists(env_dir):
            return False
            
        try:
            shutil.rmtree(env_dir)
            return True
        except Exception:
            return False
    
    def move_context(self,):
        raise NotImplementedError


    def move_env(self, 
                 target_dir=None,
                 delete_source=True):
        """
        Move a virtual environment from source_dir to target_dir.
        
        This will:
        1. Copy the entire environment 
        2. Update any paths in scripts that may reference the old location
        3. Remove the old environment if successful
        
        Args:
            source_dir: Path to the existing environment
            target_dir: Path where the environment should be moved
            
        Returns:
            bool: True if successful, False otherwise
        """
        source_dir = self.env_path

        if target_dir.split('/')[-1] != self.env_name and os.path.isdir(target_dir):
            target_dir = os.path.join(target_dir, self.env_name)
            self.env_path = target_dir
        #print(f"Moving environment from {source_dir} to {target_dir}...")

        if not source_dir or not target_dir:
            return False
            
        if not os.path.exists(source_dir):
            return False
            
        if os.path.exists(target_dir):
            return False  # Target already exists, won't overwrite
        
        #print(f"Copying environment to {target_dir}...")

        try:            
            # Copy the environment to the new location
            shutil.copytree(source_dir, target_dir)
            
            # Fix scripts that might contain the old path
            self._fix_scripts_after_move(source_dir, target_dir)
            self.directory = target_dir.rsplit('/',1)[0]
            
            if delete_source:
                shutil.rmtree(source_dir)
            
            return True
        except Exception as e:
            # If an error occurs, try to clean up the target directory
            if os.path.exists(target_dir):
                try:
                    shutil.rmtree(target_dir)
                except:
                    pass
            return False
    
    def _fix_scripts_after_move(self, old_path, new_path):
        """
        Update shebang lines and hardcoded paths in scripts after moving an environment.
        
        Args:
            old_path: Original path of the environment
            new_path: New path of the environment
        """
        # Fix scripts in bin directory
        bin_dir = os.path.join(new_path, 'bin')
        if not os.path.exists(bin_dir):
            return
            
        for filename in os.listdir(bin_dir):
            filepath = os.path.join(bin_dir, filename)
            
            # Skip if not a file or not readable
            if not os.path.isfile(filepath) or not os.access(filepath, os.R_OK):
                continue
                
            # Check if it's a text file (skip binary files)
            try:
                with open(filepath, 'r', errors='ignore') as f:
                    content = f.read(100)  # Read just the beginning
                    
                # Skip if it doesn't look like a text file
                if b'\0' in content.encode('utf-8', errors='ignore'):
                    continue
                    
                # Read the whole file
                with open(filepath, 'r', errors='ignore') as f:
                    content = f.read()
                    
                # Replace old path with new path
                if old_path in content:
                    new_content = content.replace(old_path, new_path)
                    with open(filepath, 'w') as f:
                        f.write(new_content)
            except:
                # Skip any file that causes issues
                continue


    """
    def to_dict(self,):
        return {
            "name": self.env_name,
            "directory": os.path.dirname(self.env_path) if self.env_path else None,
            "system_site_packages": self.system_site_packages, 
            "clear": self.clear, 
            "symlinks": self.symlinks,
            "upgrade": self.upgrade, 
            "with_pip": self.with_pip, 
            "prompt": self.prompt, 
            "requirements": self.requirements,
            "auto_build": True,
            "env_name": self.env_name,
            "env_path": self.env_path
        }"""
    
    @classmethod
    def from_dict(cls, **kwargs):
        return cls( **kwargs )

    def to_json(self,):
        import json
        return json.dumps(self.to_dict(),
                          indent=4)
    



