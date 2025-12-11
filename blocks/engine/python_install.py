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



def remove_wrapper(src, wrap_name='@task_node'):
    lines = src.split('\n')
    new_lines = []
    skipping = True
    
    for line in lines:
        stripped = line.strip()
        if stripped.startswith(wrap_name):
            continue
        if stripped.startswith('def '):
            skipping = False
        if skipping:continue
        
        new_lines.append(line)
    return "\n".join(new_lines)



def extract_dependencies(src):
    tree = ast.parse(src)

    name = set()
    for node in ast.walk(tree):
        if isinstance(node,ast.Name):
            name.add(node.id)
    return name


class _python_installer:

    def __post_init__(self,
                      name: str = None,
                      directory = None,
                      auto_create=False)-> None:

        try:
            self.direct_path = os.path.join(directory, name)
            self.filemanager = FileManager(base_directory=self.direct_path,
                                           auto_create=auto_create)
        except:
            #self.error =  BlockError(f'Path unknow : {path}', 'ORIGIN')
            #raise self.error.ERROR
            print('Error occurs')
        


    def __install__(self,
                    install_directory=None, 
                    **kwargs):
        print(f"Installing prototype '{self.name}' at '{self.directory}'")
        
        self._create_dir()
        self._export_code(kwargs.get('codes',self.codes))
        self._export_files(kwargs.get('files',self.files))

        

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


    # TODO: Vérifier que cela fonctionne avec des dossiers
    def _export_files(self, files):

        target_path = os.path.abspath(self.direct_path)

        for file in files:
            
            file = os.path.abspath(file)
            try:
                if os.path.isfile(file):
                    
                    dest_file = os.path.join(target_path, os.path.basename(file))
                    self.filemanager.copy_files(file, dest_file, overwrite=True)
                    
                elif os.path.isdir(file):
                    if not self.filemanager.directory_exists(file):
                        raise FileError(f"Directory {file} does not exist")
                    
                    dest_dir = os.path.join(target_path, os.path.basename(file))
                    self.filemanager.copy_files(file, dest_dir, overwrite=True)
                    
                else:
                    print(f"Warning: {file} is neither a file nor a directory")
                    
            except Exception as e:
                print(f"Error processing file {file}: {e}")
                raise FileError(f"Failed to process file {file}: {e}")
            
    
        # =====================================================================
        # TODO: Mise à jour du _register_methods avec le nouveau pathing
        # des méthodes avec la lecture et l'enregistrement des nouvelles 
        # fonctions.


        


    # TODO: Allow to write code in specified named file 
    # (sous la forme d'un dict)
    
    def _export_code(self, 
                     codes,
                     ignore_decorator=None):
        
        if ignore_decorator is None:
            ignore_decorator = []
            
        # Initialize files attribute if it doesn't exist
        if not hasattr(self, 'files'):
            self.files = []
            
        # Traitement des fonctions
        target_path = os.path.abspath(self.direct_path)

        for code in codes:
            
            try:
                def _unwrap_function(func):
                    original = func
                    
                    # First, try standard unwrapping via __wrapped__
                    while hasattr(original, '__wrapped__'):
                        original = original.__wrapped__
                    
                    # If we still have a generic wrapper, search in closure
                    if (original.__name__ == 'wrapper' and 
                            hasattr(original, '__closure__') and 
                        original.__closure__):
                        
                        for cell in original.__closure__:
                            if (hasattr(cell, 'cell_contents') and 
                                    callable(cell.cell_contents) and 
                                    hasattr(cell.cell_contents, '__name__') and
                                cell.cell_contents.__name__ != 'wrapper'):
                                original = cell.cell_contents
                                break
                    
                    return original

                # Get the original function and its name
                original_code = _unwrap_function(code)
                _name = original_code.__name__
                filename = os.path.join(target_path,f'{_name}.py')

                if filename not in self.files:
                    self.files.append(filename)

                module = inspect.getmodule(original_code)
                module_source = inspect.getsource(module)
                module_ast = ast.parse(module_source)
                module_lines = module_source.splitlines(True)

                target_name = original_code.__name__

                code_def = {
                    node.name:node 
                        for node in module_ast.body 
                            if isinstance(node,ast.FunctionDef)
                }      

                # Check if target function exists in code_def
                if target_name not in code_def:
                    print(f"Warning: Function {target_name} not found in module")
                    continue

                to_process = {target_name}
                required = set()

                while to_process:
                    current = to_process.pop()
                    required.add(current)

                    if current in code_def:
                        node = code_def[current]
                        for child in ast.walk(node):
                            if isinstance(child,ast.Call) and \
                                    isinstance(child.func,ast.Name):
                                name = child.func.id
                                if name in code_def and name not in required:
                                    to_process.add(name)
                                    
                import_nodes = [ 
                    node for node in module_ast.body 
                        if isinstance(node,ast.Import) or \
                            isinstance(node, ast.ImportFrom)
                ]
                
                def extract_source(node):
                    start = node.lineno - 1
                    end = node.end_lineno if node.end_lineno else node.lineno
                    return "".join(module_lines[start:end])
                
                def extract_decorator(node):
                    start = node.lineno - 1
                    end = node.end_lineno if node.end_lineno else node.lineno
                    block = module_lines[start:end]
                    #nb_decors = len(node.decorator_list)
                    #clean_block = block[nb_decors:]
                    return "".join(block)

                
                export_code = []
                for node in import_nodes:
                    export_code.append(extract_source(node))

                export_code.append('\n\n# === Dependant Function ===\n\n')

                for node in module_ast.body:
                    if isinstance(node,ast.FunctionDef) and node.name in required:
                        export_code.append(extract_decorator(node)+'\n')

                with open(filename,'w') as f:
                    f.write("".join(export_code))

            except Exception as e:
                print(f"Can't install {code.__name__} function: {e}")








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
