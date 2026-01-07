import os
import sys

import ast
import inspect
import textwrap

from typing import *
from abc import *
from pathlib import Path
from enum import Enum

from tools.load import *
from tools.organizer import FileManager, FileError






class InstallerPython:

    __install_type__ = 'python'

    def __post_init__(self,
                      name: str = None,
                      directory = None,
                      auto_create=False)-> None:

        try:
            self.direct_path = os.path.join(directory, name)
            self.filemanager = FileManager(base_directory=self.direct_path,
                                           auto_create=auto_create)
        except:
            print('Error occurs')
        


    def __install__(self,
                    name=None,
                    install_directory=None, 
                    **kwargs):
        if install_directory is not None:
            self.directory = os.path.abspath(install_directory)
            
        file_dir = os.path.join(self.directory,self.name)
        print(f"Installing prototype '{self.name}' at '{file_dir}'")

        self._create_dir()

        self._dataset['files'] = [
            f'{os.path.join(file_dir,self.name)}.py']

        self.export_method(
            f'{self.name}.py',
            self.direct_path,
            **self._register_methods
        )
        
        return self


    def __uninstall__(self):

        self.delete_directory()


    def _create_dir(self):

        direct_path = os.path.join(self.directory, self.name)
        print(f"Creating node directory at: {direct_path}")

        try:
            if not os.path.exists(direct_path):
                os.makedirs(direct_path, mode=0o755, exist_ok=True)
            else:
                os.chmod(direct_path, 0o755)
        except PermissionError as e:
            raise FileError(f"Permission denied creating directory {direct_path}: {e}")
        except Exception as e:
            raise FileError(f"Failed to create directory {direct_path}: {e}")

        self.direct_path = direct_path

    

    def _export_metadata(self,):
        pass

    def _export_exec(self,):
        pass
    

    # ===========================================
    # Directory management
    # ===========================================



    def delete_directory(self, directory=None) -> None:
        """
        Supprime le répertoire du block.
        """
        if directory is None:
            directory = os.path.join(self.directory, self.name)
            directory = os.path.abspath(directory)
        else:
            directory = os.path.abspath(directory)

        self.filemanager.delete_directory(directory)

    def compress(self, 
                 source: Union[str, Path] = None, 
                 destination: Union[str, Path] = None) -> None:
        """
        Compresse le contenu du répertoire source dans une archive ZIP.

        Args:
            source (Union[str, Path]): Chemin du répertoire à compresser.
            destination (Union[str, Path]): Chemin de l'archive ZIP de destination.
        """
        if source is None:
            source = os.path.join(self.directory, self.name)

        if destination is None:
            destination = os.path.join(self.directory, f"{self.name}.zip")

        self.filemanager.create_zip(source, destination)

    def decompress(self, 
                   source: Union[str, Path], 
                   destination: Union[str, Path] = '') -> None:
        """
        Décompresse une archive ZIP dans le répertoire de destination.

        Args:
            source (Union[str, Path]): Chemin de l'archive ZIP à décompresser.
            destination (Union[str, Path]): Chemin du répertoire de destination.
        """
        self.filemanager.extract_zip(source, 
                              destination)


    def rename(self, new_name: str) -> None:
        """
        Rename the block.
        """
        old_name = os.path.join(self.directory, self.name)
        new_path = os.path.join(self.directory, new_name)

        if os.path.exists(new_path):
            print(f"Le répertoire {new_path} existe déjà.")
            return
        
        
        self.filemanager.rename(old_name, new_path)
        self.name = new_name

    def compose(self, 
                filename,
                content = None,
                encoding='utf-8',
                append=False):
        """
        Compose a file with the given content.
        """
        
        self.filemanager.write_file(filename, 
                             content,
                             encoding=encoding,
                             append=append,
                             auto_create=True)

    def move(self,
             destination,
             overwrite: bool = False) -> None:

        # Destination existe ?
        if os.path.exists(destination): 
            print(f"Le répertoire {destination} existe déjà.")
            return  

        _origin     = os.path.join(self.directory, self.name)
        destination = os.path.abspath(os.path.join(destination,self.name))
        
        # Déplacement
        self.filemanager.move_files(_origin, 
                             destination, 
                             overwrite=overwrite)



class InstallerPythonWorkflow:

    __install_type__ = 'pythonWorkflow'

    def __post_init__(self,
                      name: str = None,
                      directory = None,
                      auto_create=False)-> None:

        try:
            self.direct_path = os.path.join(directory, name)
            self.filemanager = FileManager(base_directory=self.direct_path,
                                           auto_create=auto_create)
        except Exception as e:
            print(f'Error occurs: {e}')
        


    def __install__(self,
                    name=None,
                    install_directory=None, 
                    **kwargs):
        if install_directory is not None:
            self.directory = os.path.abspath(install_directory)
            
        file_dir = os.path.join(self.directory,self.name)
        print(f"Installing workflow '{self.name}' at '{file_dir}'")

        self._create_dir()
        return self


    def __uninstall__(self):
        '''
        Supprime le répertoire du block.
        '''
        self.delete_directory()
        



    def _create_dir(self):

        direct_path = os.path.join(self.directory, self.name)
        print(f"Creating workflow directory at: {direct_path}")

        try:
            if not os.path.exists(direct_path):
                os.makedirs(direct_path, mode=0o755, exist_ok=True)
            else:
                os.chmod(direct_path, 0o755)
        except PermissionError as e:
            raise FileError(f"Permission denied creating directory {direct_path}: {e}")
        except Exception as e:
            raise FileError(f"Failed to create directory {direct_path}: {e}")

        self.direct_path = direct_path

    

    def _export_metadata(self,):
        pass

    def _export_exec(self,):
        pass
    

    # ===========================================
    # Directory management
    # ===========================================



    def delete_directory(self, directory=None) -> None:
        """
        Supprime le répertoire du block.
        """
        if directory is None:
            directory = os.path.join(self.directory, self.name)
            directory = os.path.abspath(directory)
        else:
            directory = os.path.abspath(directory)

        self.filemanager.delete_directory(directory)



