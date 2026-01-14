import os
import sys

import ast
import inspect
import textwrap
import pickle

from typing import *
from abc import *
from pathlib import Path
from enum import Enum

from tools.load import *
from tools.organizer import FileManager, FileError


class Installer:

    def __init__(
            self,
            object=None, 
            *,
            directory=None,
            auto=False):
        
        self.object = object     
        self.auto_create = auto
        self.path_to_install = directory or os.path.abspath(object.directory)

        self.filemanager = FileManager(
            base_directory=os.path.join(
                self.path_to_install, 
                self.object.name ),
            auto_create=auto )



    def to_config(self):
        return {
            'auto': self.auto_create,
        }


    def update_metadata(
            self,
            name: str = None,
            directory = None,
            format: str = 'json',):
        
        self.export_metadata(
            name=name,
            directory=directory,
            format=format)
        
        
    def export_metadata(
            self, 
            name: str = None,
            directory = None,
            format: str = 'json',):

        filename = f'{self.object.__ntype__}.{format}'        

        if format == 'json':
            content = self.object.to_json()
        elif format == 'csv':
            content = self.object.to_csv()
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        #print('\nContent of Metadata file :\n',content)

        _dir = os.path.join(
            directory or self.path_to_install, 
            name or self.object.name,
            filename
        )

        self.filemanager.write_file(
            _dir,
            content
        )


    @staticmethod
    def import_metadata(
            name: str = None,
            directory = None,
            ntype: str = 'prototype',
            format: str = 'json',):
        
        filename = f'{ntype}.{format}'
        abs_directory = os.path.abspath(directory)
        _dir = os.path.join(abs_directory, name, filename )

        filemanager = FileManager(
            base_directory=os.path.join( abs_directory, name ),
            auto_create=False )
        
        content = filemanager.read_json(_dir)
        return content





    def __install__(self, 
                    **kwargs):
        print("Default install: No action taken.")
        return self

    def __uninstall__(self,):
        print("Default uninstall: No action taken.")




    # ===========================================
    # Directory management
    # ===========================================



    def _create_dir(self, 
                    directory=None):

        if directory is not None:
            path_to_install = os.path.abspath(directory)

        print(f"Creating node directory at: {path_to_install}")

        try:
            if not os.path.exists(path_to_install):
                os.makedirs(path_to_install, mode=0o755, exist_ok=True)
            else:
                os.chmod(path_to_install, 0o755)
        except PermissionError as e:
            raise FileError(f"Permission denied creating directory {path_to_install}: {e}")
        except Exception as e:
            raise FileError(f"Failed to create directory {path_to_install}: {e}")

        #self.path_to_install = path_to_install



    def delete_directory(self, directory=None) -> None:
        """
        Supprime le répertoire du block.
        """
        if directory is None:
            directory = os.path.join(self.path_to_install,self.object.name)
            #directory = os.path.abspath(directory)
        else:
            directory = os.path.abspath(directory)

        print(f"Deleting directory at: {directory},{self.path_to_install}")
        self.filemanager.delete_directory(directory)

    def compress(self, 
                 zipname: str = None,
                 source: Union[str, Path] = None, 
                 destination: Union[str, Path] = None,) -> None:
        """
        Compresse le contenu du répertoire source dans une archive ZIP.

        Args:
            source (Union[str, Path]): Chemin du répertoire à compresser.
            destination (Union[str, Path]): Chemin de l'archive ZIP de destination.
        """
        if source is None:
            source = self.path_to_install

        if zipname is None:
            zipname = f"{self.object.name}.zip"

        source = os.path.join(source, self.object.name)

        if destination is None:
            destination = os.path.join(
                os.path.abspath(self.object.directory), f"{zipname}")

        print(f"Compressing from {source} to {destination}")

        self.filemanager.create_zip(source, destination)

    def decompress(self, 
                   zipname: str = None,
                   source: Union[str, Path] = None, 
                   destination: Union[str, Path] = None) -> None:
        """
        Décompresse une archive ZIP dans le répertoire de destination.

        Args:
            source (Union[str, Path]): Chemin de l'archive ZIP à décompresser.
            destination (Union[str, Path]): Chemin du répertoire de destination.
        """
        if zipname is None:
            zipname = f"{self.object.name}.zip"

        if source is None:
            source = self.path_to_install

        source = os.path.join(source, zipname)

        if destination is None:
            destination =  self.path_to_install
        
        print(f"Decompressing from {source} to {destination}")

        self.filemanager.extract_zip(source, 
                              destination)


    def rename(self, new_name: str) -> None:
        """
        Rename the block.
        """
        old_name = os.path.join(self.path_to_install, self.object.name)
        new_path = os.path.join(self.path_to_install, new_name)

        print(f"Renaming block from {old_name} to {new_path}")
        
        if os.path.exists(new_path):
            print(f"Le répertoire {new_path} existe déjà.")
            return
        
        self.filemanager.rename(old_name, new_path)
        self.object.name = new_name

        files = self.object._dataset.get('files', [])
        updated_files = []

        for file in files:
            updated_file = file.replace(old_name, new_path)
            updated_files.append(updated_file)

        self.object._dataset['files'] = updated_files

        self.update_metadata()


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
             erase_source: bool = False,
             overwrite: bool = False) -> None:

        # Destination existe ?
        #if os.path.exists(destination): 
        #    print(f"Le répertoire {destination} existe déjà.")
        #    return  
        _source = os.path.join(self.path_to_install, self.object.name)
        _destination = os.path.abspath(
            os.path.join(destination,self.object.name))
        
        # Déplacement
        self.filemanager.move_files(
            _source, 
            _destination, 
            overwrite=overwrite)

        if erase_source:
            self.delete_directory(_source)

        self.path_to_install = os.path.abspath(destination)

        print(f"Block moved to {self.path_to_install}")









class InstallerPython(Installer):

    def __init__(
            self,
            object=None, 
            *,
            directory=None,
            auto=False):
        super().__init__(
            object=object,
            directory=directory,
            auto=auto)
        
        
    def export_environ(
            self,
            directory,
            format='pickle'):
        
        structural_object = {
            'installer':self.object.installer.__class__,
            'installer_config':self.object.installer.to_config(),
            'environment':self.object.environment.__class__,
            'environment_config':self.object.environment.to_config() or {},
            'executor':self.object.executor.__class__,
            'executor_config':self.object.executor.to_config() or {},
        }

        struct = os.path.join(directory, '.environ')

        with open(struct,'wb') as f:
            pickle.dump(structural_object, f)

    
    
    @staticmethod
    def import_structure(
            name: str = None,
            directory = None,):
        
        abs_directory = os.path.abspath(directory)
        struct = os.path.join(
            abs_directory, 
            name,
            '.environ'
        )

        with open(struct,'rb') as f:
            structural_object = pickle.load(f)
        return structural_object


    def __install__(
            self, 
            format='json',
            *,
            files=[],
            directory=None,
            extension='py',
            **kwargs):
        
        if directory is not None:
            directory = os.path.abspath(directory)
        
        _path_to_install = os.path.join(
            directory or self.path_to_install, 
            self.object.name
        )

        self._create_dir(directory=_path_to_install)

        self.object._dataset['files'] = [ 
            f'{os.path.join(_path_to_install,self.object.name)}.{extension}'
        ]

        self.export_metadata(_path_to_install,
                             format=format)

        files = self.object._dataset['files'] or files

        for file in files:
            self.object.export_method(
                file,
                _path_to_install,
                **self.object._register_methods
            )

        self.export_environ(_path_to_install,
                              format='pickle')
            
        
    @staticmethod
    def __load__(
            *,
            name: str,
            format='json',
            ntype: str = 'prototype',
            extension='py',
            directory=None,):
        
        if directory is not None:
            directory = os.path.abspath(directory)

        content = InstallerPython.import_metadata(
            name=name,
            directory=directory,
            ntype=ntype,
            format=format
        )

        structure = InstallerPython.import_structure(
            name=name,
            directory=directory,
        )

        return (content, structure)



        
    def __uninstall__(self, directory=None):
        print(f"Uninstalling block '{self.object.name}' from '{self.path_to_install}'")
        self.delete_directory(
            directory=directory
        )








        
###############################################################################
# Installer for Workflow 
###############################################################################


class InstallerPythonWorkflow(Installer):

    def __init__(
            self,
            object=None, /,
            *,
            directory=None,
            auto=False):
        
        self.object = object     
        self.auto_create = auto
        self.path_to_install = directory or os.path.abspath(object.directory)

        self.filemanager = FileManager(
            base_directory=os.path.join(
                self.path_to_install, 
                self.object.name ),
            auto_create=auto )
        

    def export_environ(
            self,
            directory,
            format='pickle'):
        
        structural_object = {
            'installer':self.object.installer.__class__,
            'installer_config':self.object.installer.to_config(),
            'environment':self.object.environment.__class__,
            'environment_config':self.object.environment.to_config() or {},
            'executor':self.object.executor.__class__,
            'executor_config':self.object.executor.to_config() or {},
            'graphics':self.object.graphics.__class__,
            'graphics_config':self.object.graphics.to_config(),
            'communicate':self.object.communicate.__class__,
            'communicate_config':{},
            'interface':self.object.interface,
            'queue':self.object.queue.__class__,
        }

        struct = os.path.join(directory, '.environ')

        with open(struct,'wb') as f:
            pickle.dump(structural_object, f)

    @staticmethod
    def import_environ(
            name: str = None,
            directory = None,):
        
        abs_directory = os.path.abspath(directory)
        struct = os.path.join(
            abs_directory, name, '.environ' )

        with open(struct,'rb') as f:
            structural_object = pickle.load(f)

        structural_object['queue'] = structural_object.get('queue', None)()
        return structural_object



    def export_register_nodes(self,
                              directory,
                              format='pickle'):
        
        def build_register_nodes():
            register_nodes = self.object._register_nodes
            _regist = {}

            for label,register_node in register_nodes.items():
                node = register_node['node'].name
                method_name = register_node['function_name']
                ntype = register_node['ntype']
                transformer = register_node['transformer']
                directory = register_node['directory']
                attributes = register_node.get('attributes',{})

                _regist.update({label:{
                    'node': node,
                    'directory': directory,
                    'ntype': ntype,
                    'method_name': method_name,
                    'transformer': transformer,
                    'attributes': attributes,
                }})
            return _regist

        register_nodes = build_register_nodes()

        struct = os.path.join(directory, '.register')
        with open(struct,'wb') as f:
            pickle.dump(register_nodes, f)

    @staticmethod
    def import_register_nodes(
            name: str = None,
            directory = None,):
        
        abs_directory = os.path.abspath(directory)
        struct = os.path.join(
            abs_directory, name, '.register' )
        
        with open(struct,'rb') as f:
            register_nodes = pickle.load(f)
        return register_nodes




    def __install__(
            self, 
            format='json',
            *,
            files=[],
            directory=None,
            extension='py',
            **kwargs):
        
        if directory is not None:
            directory = os.path.abspath(directory)
        
        _path_to_install = os.path.join(
            directory or self.path_to_install, 
            self.object.name
        )

        self._create_dir(directory=_path_to_install)


        self.export_metadata(_path_to_install,
                             format=format)

        self.export_environ(_path_to_install,
                              format='pickle')
            
        self.export_register_nodes(_path_to_install,
                                   format='pickle')
        
    @staticmethod
    def __load__(
            *,
            name: str,
            format='json',
            ntype: str = 'workflow',
            extension='py',
            directory=None,):
        
        if directory is not None:
            directory = os.path.abspath(directory)

        content = InstallerPythonWorkflow.import_metadata(
            name=name,
            directory=directory,
            ntype=ntype,
            format=format
        )

        structure = InstallerPythonWorkflow.import_environ(
            name=name,
            directory=directory,
        )

        register = InstallerPythonWorkflow.import_register_nodes(
            name=name,
            directory=directory,
        )

        return (content, structure, register)
    
    def __uninstall__(self, directory=None):
        print(f"Uninstalling workflow '{self.object.name}' from '{self.path_to_install}'")
        self.delete_directory(
            directory=directory
        )



