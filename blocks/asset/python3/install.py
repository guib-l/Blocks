import os
import sys

import ast
import inspect
import textwrap
import pickle

from typing import *
from abc import *
from pathlib import Path

from tools.load import *
from tools.organizer import FileManager

from blocks.utils.logger import *

from blocks.utils.exceptions import InstallError,ErrorCodeInstall
from blocks.utils.exceptions import safe_operation

from blocks.engine.installer import Installer






class InstallerPython(Installer):

    def __init__(
            self,
            object=None, 
            *,
            directory=None,
            auto=False):
        """
        Installer for Python Blocks

        Args:
            object : Block object to install
            directory : installation directory
            auto : auto create directory if not exists
        
        Exemple:
            Basic usage :
            >>> installer = InstallerPython(
            ...     object=block,   
            ...     directory='/path/to/install',
            ...     auto=True )
            >>> installer.__install__()
        
        Raises:
            InstallError: If installation fails
            
        """
        
        logger.debug('Enter in python Installer module')

        super().__init__(
            object=object,
            directory=directory,
            auto=auto)
        
        
    def export_environ(
            self,
            directory,
            format='pickle'):
        """
        Export environment of Block
        
        Args:
            directory : installation directory
            format : format of export (pickle)
        
        """
        structural_object = {
            'installer':self.object.installer.__class__,
            'installer_config':self.object.installer.to_config(),
            'environment':self.object.environment.__class__,
            'environment_config':self.object.environment.to_config() or {},
            'executor':self.object.executor.__class__,
            'executor_config':self.object.executor.to_config() or {},
        }

        struct = os.path.join(directory, '.environ')

        self.data_dumps(
            structural_object,
            struct,
            format,
            encode="wb"
        )
    
    @staticmethod
    def import_structure(
            name: Optional[str] = None,
            directory: Optional[str] = None,):
        """
        Import environment structure of Block

        Args:
            name : name of Block
            directory : installation directory
        
        Returns:
            structural_object : dict of environment structure
        
        Raises:
            InstallError: If import fails
        """
        
        abs_directory = os.path.abspath(directory or '.')

        struct = os.path.join(
            abs_directory, 
            name or '',
            '.environ'
        )

        try:
            with open(struct,'rb') as f:
                structural_object = pickle.load(f)
        except:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_ENVIRON,
                message=f"Cannot import environment of Node"
            )
        return structural_object


    def __install__(
            self, 
            format='json',
            *,
            files=[],
            directory=None,
            extension='py',
            **kwargs) -> 'InstallerPython':
        """
        Install Block

        Args:
            format (str): format of metadata export (json)
            files (list): list of files to export
            directory (str): installation directory
            extension (str): file extension of exported files

        Raises:
            InstallError: If installation fails
        """
        
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
        return self
            
        
    @staticmethod
    def __load__(
            *,
            name: str,
            format='json',
            ntype: str = 'prototype',
            extension='py',
            directory=None,
            **kwargs):
        
        logger.info(f"Load of installed block {name}")
        
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
        logger.info(f"Uninstalling block '{self.object.name}' from '{self.path_to_install}'")
        
        self.delete_directory(
            directory=directory
        )








        
###############################################################################
# Installer for Workflow 
###############################################################################




class InstallerPythonWorkflow(Installer):

    def __init__(
            self,
            object: Any = None, /,
            *,
            directory: Optional[str] = None,
            auto: bool = False):
        
        self.object = object     
        self.auto_create = auto
        self.path_to_install: str = directory or os.path.abspath(str(object.directory))

        self.filemanager = FileManager(
            base_directory=os.path.join(
                self.path_to_install, 
                self.object.name ),
            auto_create=auto )
        

    def export_environ(
            self,
            directory,
            format='pickle'):

        with safe_operation(
                'Export environment of Workflow',
                ErrorCodeInstall.INSTALL_ERROR_ENVIRON,
                ERROR=InstallError):
            

            
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
                'buffer':self.object.buffer.__class__,
            }

            struct = os.path.join(directory, '.environ')

            self.data_dumps(
                structural_object,
                struct,
                format,
                encode="wb"
            )
            
    @staticmethod
    def import_environ(
            name: Optional[str] = None,
            directory: Optional[str] = None,):
        
        abs_directory = os.path.abspath(directory or '.')
        struct = os.path.join(
            abs_directory, name or '', '.environ' )

        with open(struct,'rb') as f:
                structural_object = pickle.load(f)
        try:
            with open(struct,'rb') as f:
                structural_object = pickle.load(f)
        except:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_ENVIRON,
                message=f"Cannot import environment of Workflow"
            )

        structural_object['buffer'] = (structural_object.get('buffer') or (lambda: None))()
        return structural_object



    def export_register_nodes(self,
                              directory,
                              format='pickle'):
        import copy
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
                    'transformer':transformer,
                    'attributes': attributes,
                }})
            return _regist

        try:
            register_nodes = build_register_nodes()
        except:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_BUILD,
                message=f"Cannot import environment of Workflow"
            )
        
        struct = os.path.join(directory, '.register')
        
        self.data_dumps(
            register_nodes,
            struct,
            format,
            encode="wb"
        )


    @staticmethod
    def import_register_nodes(
            name: Optional[str] = None,
            directory: Optional[str] = None,
            format: str = "pickle"):
        
        abs_directory = os.path.abspath(directory or '.')
        struct = os.path.join(
            abs_directory, name or '', '.register' )
        

        if format=='pickle':
            with open(struct,'rb') as f:
                register_nodes = pickle.load(f)
        else:
            raise InstallError(
                code=ErrorCodeInstall.INSTALL_ERROR_DESERIALIZATION,
                message=f"Unknow format {format}: accepted: [pickle,]"
            )
        return register_nodes


    


    def __install__(
            self, 
            format='json',
            *,
            files=[],
            directory=None,
            extension='py',
            **kwargs) -> 'InstallerPythonWorkflow':
        
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
        return self
        
    @staticmethod
    def __load__(
            *,
            name: str,
            format='json',
            ntype: str = 'workflow',
            extension='py',
            directory=None,):
        
        logger.info(f"Load of installed workflow {name}")

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
        logger.info(f"Uninstalling workflow '{self.object.name}' from '{self.path_to_install}'")
        
        self.delete_directory(
            directory=directory
        )






