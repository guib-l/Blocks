import os
import sys
import io
import uuid
import zipfile
import json
from datetime import *
from copy import copy, deepcopy
import csv
from typing import *
from abc import *
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional, Union, Callable, Iterator, BinaryIO, TextIO

from .dataset import DataSet
from copy import copy, deepcopy

from blocks.base.baseBlock import BaseBlock
from typing import Any, Dict, TypeVar, Optional
from blocks.base.version import VersionManager
from blocks.base.organizer import FileManager, FileError

from blocks.base.encoder import BaseBlockJSONEncoder


from blocks.base.signal import Signal

from blocks.socket.interface import MESSAGE

from enum import Enum

T = TypeVar('T', bound='Block')



def export_metadata(block, filename: str, format: str) -> None:
    """
    Export metadata from a Block instance to a file.
    Args:
        block (Block): The Block instance to export metadata from.
        filename (str): The name of the file to export to (without extension).
        format (str): The format to export the metadata in ('json', 'csv', etc.).
    """
    block.export_metadata(filename=filename, format=format)



class BlockErrorType(str, Enum):
    INPUT       = "Wrong input"
    OUTPUT      = "Wrong output"
    DESTINATION = "Destination of Block unknown"
    DIRECTORY   = "Path of Block unknown"
    ORIGIN      = "Origin path of Block unknown"
    VERSION     = "Version does not match"
    LANGUAGE    = "Language not supported"



class BlockError(Exception):

    err_type = None

    def __init__(self, 
                 message: str = "Block error occurred", 
                 err_type: Optional[str] = None):
        
        self._set_error_type(err_type)

        if err_type is not None:
            message = f"{message}: Error Block : '{self.err_type}'"
        else:
            message = f"{message}: Error Block unknow"

        super().__init__(message)

    def _set_error_type(self, value):

        if value in [s.name for s in BlockErrorType]:
            self.err_type = BlockErrorType[value]
        



class Block(BaseBlock):

    _mandatory_attributes = ['load']

    __ntype__ = "block"

    def __init__(self, 
                 id=None, 
                 name="default",
                 version="0.0.1",
                 path='.',
                 authors=["Anonymous"],
                 files=[],
                 data={},
                 doc=None,
                 type="blocks",
                 SIGNAL=None,
                 _build=False,
                 **kwargs):
        try:
            origin = os.path.abspath(path)
            path = os.path.join(path, name)

            self.fman = FileManager(base_directory=path,
                                    auto_create=_build)
        except:
            self.error =  BlockError(f'Path unknow : {path}', 'ORIGIN')
            raise self.error.ERROR
        
        self.__SIGNAL__ = 'INITIALIZED'

        super().__init__(id=id,
                         name=name,
                         version=version,
                         path=origin,
                         authors=authors,
                         files=files,
                         data=data,
                         doc=doc,
                         **kwargs)
        if _build:
            export_metadata(self, type, 'json')




    # -----------------------------------------------------
    # Export all metadata in block.json
    
    @final
    def export_metadata(self,
                        filename='blocks',
                        format='json'):
        
        if os.path.splitext(filename)[1] != '':
            if os.path.splitext(filename)[1] != f".{format}":
                raise ValueError("Le nom de fichier doit se terminer par l'extension correspondant au format spécifié.")    
            
        content = None

        if format == 'json':
            content = self.to_json()
        elif format == 'csv':
            content = self.to_csv()
        else:
            raise ValueError(f"Unsupported format: {format}")

        if content:

            path = os.path.join(self.path,
                                self.name,
                                f"{filename}.{format}")
            
            from blocks.base.encoder import NodeJSONEncoder
            #obj = json.dumps(content, 
            #                 indent=4, 
            #                 cls=NodeJSONEncoder)
            
            with open(path, "w") as f:
                f.write(content)

    # -----------------------------------------------------
    # Serialization

    def to_csv(self):
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(self._dataset.keys())
        writer.writerow(self._dataset.values())
        return output.getvalue()

    def to_json(self):
        return json.dumps(self._dataset, 
                          indent=4, 
                          cls=BaseBlockJSONEncoder)

    def to_dict(self,):
        return self._dataset


    # -----------------------------------------------------
    # Load methods

    @classmethod
    def load(cls): ...

    @classmethod
    def load_from_dict(cls, data):
        obj = cls(**data)
        obj.signal = 'LOADED'
        return obj

    @classmethod
    def load_from_directory(cls, 
                            name=None,
                            path=None,
                            metadata_file='blocks',
                            format='json',
                            encoding='utf-8',
                            **kwargs):
       
        path = os.path.abspath(path)
        full_path = os.path.join(path, name, 
                                 metadata_file + f'.{format}')

        with open(full_path, 'r', encoding=encoding) as file:
            content = file.read()

        data = json.loads(content)

        data.update(kwargs)

        obj = cls(**data)
        obj.signal = 'LOADED'
        return obj


    # -----------------------------------------------------
    # Copy / Deepcopy
    def copy(self):
        return type(self)(**self._dataset)

    def __copy__(self):
        return self.copy()
    
    def deepcopy(self):
        return type(self)(**deepcopy(self._dataset))
    
    def __deepcopy__(self, memo):
        return self.deepcopy()


    # -----------------------------------------------------
    # Versionnning

    def update_version(major=None,minor=None,patch=None):
        pass

    @abstractmethod
    def publish(self,): ...

    @abstractmethod
    def compare(self,): ...

    @abstractmethod
    def archive(self,): ...

    @abstractmethod
    def extract(self,): ...


    # -----------------------------------------------------
    # Gestion fichiers
    def rename(self, new_name: str) -> None:
        """
        Rename the block.
        """
        old_name = os.path.join(self.path, self.name)
        new_path = os.path.join(self.path, new_name)

        if os.path.exists(new_path):
            print(f"Le répertoire {new_path} existe déjà.")
            return
        
        
        self.fman.rename(old_name, new_path)
        self.name = new_name

    def compose(self, 
                filename,
                content = None,
                encoding='utf-8',
                append=False):
        """
        Compose a file with the given content.
        """
        
        self.fman.write_file(filename, 
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

        _origin     = os.path.join(self.path, self.name)
        destination = os.path.abspath(os.path.join(destination,self.name))
        
        # Déplacement
        self.fman.move_files(_origin, 
                             destination, 
                             overwrite=overwrite)

    def delete_directory(self, directory=None) -> None:
        """
        Supprime le répertoire du block.
        """
        if directory is None:
            directory = os.path.join(self.path, self.name)
        else:
            directory = os.path.abspath(directory)
        
        self.fman.delete_directory(directory)

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
            source = os.path.join(self.path, self.name)

        if destination is None:
            destination = os.path.join(self.path, f"{self.name}.zip")

        self.fman.create_zip(source, destination)

    def decompress(self, 
                   source: Union[str, Path], 
                   destination: Union[str, Path] = '') -> None:
        """
        Décompresse une archive ZIP dans le répertoire de destination.

        Args:
            source (Union[str, Path]): Chemin de l'archive ZIP à décompresser.
            destination (Union[str, Path]): Chemin du répertoire de destination.
        """
        self.fman.extract_zip(source, 
                              destination)


