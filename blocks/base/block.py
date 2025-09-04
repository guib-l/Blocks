import os
import sys
import io
import uuid
import zipfile
import json
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

T = TypeVar('T', bound='Block')


default_block = {
    "id": None,
    "name": None,
    "langage": 'other',
    "location": ".",
    "description": None,
    "doc": None,
    "tags": None,
    "authors": ["Anonymous"],
    "references": None,
    "license": "MIT",
    "version": "1.0.0",
    "date": None,
}

def export_metadata(block, filename: str, format: str) -> None:
    """
    Export metadata from a Block instance to a file.
    Args:
        block (Block): The Block instance to export metadata from.
        filename (str): The name of the file to export to (without extension).
        format (str): The format to export the metadata in ('json', 'csv', etc.).
    """
    block.export_metadata(filename=filename, format=format)


class Block(BaseBlock):

    _mandatory_attributes = ['install',
                             'uninstall',
                             'load']

    def __init__(self, 
                 id=None, 
                 name="default",
                 version="0.0.1",
                 path=None,
                 authors=["Anonymous"],
                 files=[],
                 data={},
                 doc=None,
                 BUILD_BLOCK=True,
                 **kwargs):

        self.fman = FileManager(base_directory=path,
                                auto_create=BUILD_BLOCK)

        super().__init__(id=id,
                         name=name,
                         version=version,
                         path=path,
                         authors=authors,
                         files=files,
                         data=data,
                         doc=doc,
                         **kwargs)
        
        if BUILD_BLOCK:
            export_metadata(self, "blocks", 'json')

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

            path = os.path.join(self.path,f"{filename}.{format}")
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
    # Install methods
    
    @abstractmethod
    def install(self,): ...

    @abstractmethod
    def uninstall(self,): ...


    # -----------------------------------------------------
    # Load methods

    @classmethod
    def load(cls): ...

    @classmethod
    def load_from_dict(cls, data):
        return cls(**data)

    @classmethod
    def load_from_directory(cls, 
                            path=None,
                            metadata_file='block_metadata',
                            format='json',
                            encoding='utf-8'):
        
        assert path!=None, FileError('No directory found !')

        full_path = path + metadata_file + f'.{format}'
        
        with open(full_path, 'r', encoding=encoding) as file:
            content = file.read()
        
        data = json.loads(content)
        return cls(**data)

    # Copy / Deepcopy
    def __copy__(self,):
        pass

    def __deepcopy__(self,):
        pass

    # -----------------------------------------------------
    # Versionnning

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
             source,
             destination) -> None:
        # Destination existe ?
        
        # Compression du dossier
        
        # Déplacement
        
        # Décompression du dossier 

        pass

    def compress(self, 
                 source: Union[str, Path], 
                 destination: Union[str, Path]) -> None:
        """
        Compresse le contenu du répertoire source dans une archive ZIP.

        Args:
            source (Union[str, Path]): Chemin du répertoire à compresser.
            destination (Union[str, Path]): Chemin de l'archive ZIP de destination.
        """
        self.fman.create_zip(source, destination)

    def decompress(self, source: Union[str, Path], destination: Union[str, Path]) -> None:
        """
        Décompresse une archive ZIP dans le répertoire de destination.

        Args:
            source (Union[str, Path]): Chemin de l'archive ZIP à décompresser.
            destination (Union[str, Path]): Chemin du répertoire de destination.
        """
        self.fman.extract_zip(source, destination)


