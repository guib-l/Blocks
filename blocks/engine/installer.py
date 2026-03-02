import os
import pickle

from typing import *
from abc import *
from pathlib import Path

from tools.load import *
from tools.organizer import FileManager

from blocks.utils.logger import *

from blocks.utils.exceptions import InstallError,ErrorCodeInstall
from blocks.utils.exceptions import safe_operation






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
        with safe_operation(
                'Setup config serialization',
                ErrorCodeInstall.INSTALL_ERROR_CONFIG,
                InstallError):
            
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
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_METADATA,
                message=f"Unsupported format: {format}"
            )        

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
        
        with safe_operation(
                'Import metadata',
                ErrorCodeInstall.INSTALL_ERROR_METADATA,
                ERROR=InstallError):
            
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
        logger.info("Default install: No action taken.")
        return self

    def __uninstall__(self,):
        logger.info("Default uninstall: No action taken.")
        ...



    # ===========================================
    # Directory management
    # ===========================================



    def _create_dir(self, 
                    directory=None):

        if directory is not None:
            path_to_install = os.path.abspath(directory)

        logger.info(f"Creating node directory at: {path_to_install}")

        try:
            if not os.path.exists(path_to_install):
                os.makedirs(path_to_install, mode=0o755, exist_ok=True)
            else:
                os.chmod(path_to_install, 0o755)
        except PermissionError as e:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_FILENAME,
                message=f"Permission denied creating directory {path_to_install}: {e}",
                cause=e,
            )
        except Exception as e:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_FILENAME,
                message=f"Failed to create directory {path_to_install}: {e}",
                cause=e,
            )
        finally:
            logger.info(f"Created directory at {path_to_install}")



    def delete_directory(self, directory=None) -> None:
        """
        Supprime le répertoire du block.
        """
        if directory is None:
            directory = os.path.join(self.path_to_install,self.object.name)
        else:
            directory = os.path.abspath(directory)

        logger.info(f"Deleting directory at: {directory},{self.path_to_install}")
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

        self.filemanager.create_zip(source, destination)

        logger.info(f"Compressing from {source} to {destination}")


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

        self.filemanager.extract_zip(source, 
                              destination)
        
        logger.info(f"Decompressing from {source} to {destination}")


    def rename(self, new_name: str) -> None:
        """
        Rename the block.
        """
        old_name = os.path.join(self.path_to_install, self.object.name)
        new_path = os.path.join(self.path_to_install, new_name)
        
        if os.path.exists(new_path):
            logger.warning(f"Le répertoire {new_path} existe déjà.")
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

        logger.info(f"Renaming block from {old_name} to {new_path}")


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

        _source = os.path.join(self.path_to_install, self.object.name)
        _destination = os.path.abspath(
            os.path.join(destination,self.object.name))
        
        self.filemanager.move_files(
            _source, 
            _destination, 
            overwrite=overwrite)

        if erase_source:
            self.delete_directory(_source)
            logger.info(f"Source has been erased.")

        self.path_to_install = os.path.abspath(destination)

        logger.info(f"Block moved to {self.path_to_install}")


    def data_dumps(
            self,
            data,
            filename=None,
            format="pickle",
            encode="wb",
            **kwargs):
        

        if format=='pickle':
            with open(filename,encode) as f:
                pickle.dump(data, f)
        else:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_ENVIRON,
                message=f"Unknow format {format}: accepted: [pickle,]"
            )

    def data_loads(
            self,
            filename=None,
            format="pickle",
            encode="wb",
            **kwargs):
        
        if format=='pickle':
            with open(filename,encode) as f:
                data = pickle.loads(data, f)
        else:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_ENVIRON,
                message=f"Unknow format {format}: accepted: [pickle,]"
            )
        return data

