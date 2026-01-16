import os
import sys
import json

from typing import *
from abc import *
from pathlib import Path
from enum import Enum
import inspect

from tools.serializable import SerializableMixin

from blocks.base import block
from blocks.base import BLOCK_PATH
from blocks.engine.installerPy import Installer,InstallerPython,InstallerPythonWorkflow


from blocks.base.register import Register, MethodObjects

from blocks.engine.execute import Execute
from blocks.engine.environment import EnvironMixin,Environment
from blocks.engine import ENVIRONMENT_TYPE

from blocks.base import safe_operation


class INSTALLER:
    NONE     = None
    DEFAULT  = Installer
    PYTHON   = InstallerPython
    WORKFLOW = InstallerPythonWorkflow



class PrototypeErrorType(str, Enum):
    PROCESSING  = "PROCESSING"
    INSTALLER   = "INSTALLER"
    UNINSTALLER = "UNINSTALLER"
    LOADING     = "LOADING"
    SAVING      = "SAVING"
    BUILD       = "BUILD"
    EXECUTION   = "EXECUTION"
    DIRECTORY   = "DIRECTORY"
    UNKNOWN     = "UNKNOWN"

class PrototypeError(Exception):
    """Base exception for Prototype-related errors."""

    def __init__(self, 
                 err_type: Optional[PrototypeErrorType] = None,
                 message: Optional[Dict[str, Any]] = None):
        
        if err_type is not None:
            full_message = f"{err_type}\n{err_type.value}"
            if message:
                full_message += f": {message}"
            
        else:
            full_message = f"{message}: Unknown error type"

        super().__init__(full_message)







class Prototype(block.Block,Register):

    __ntype__ = "prototype"

    __slots__ = [
        'installer',
        'environment',
        'executor',
    ]

    def __init__(
            self,
            *,
            installer = None,
            environment = None,
            executor = None,
            **config
        ):
        
        self.environment = environment(**config.pop('environment_config'))

        exec_config = config.pop('executor_config')
        if executor is None:
            self.executor = Execute(backend='default',
                                    build_backend=True)
        else:
            self.executor = executor(**exec_config)


        methods = config.pop('methods',[])
        files   = config.pop('files',[])


        if hasattr(self,'init_register'):
            
            self.init_register(
                config.pop('allowed_name',[]),
                methods=methods, 
                files=files,
            )

        install_config = config.pop('installer_config')

        super().__init__(allowed_name = self.allowed_name,
                         **config)

        self.installer = installer(
            self,
            **install_config
        )

        
    def to_dict(self,):

        _dict = super().to_dict()
        _dict.update({
            'installer':self.installer.__class__,
            'installer_config':self.installer.to_config(),
            'environment':self.environment.__class__,
            'environment_config':self.environment.to_config() or {},
            'executor':self.executor.__class__,
            'executor_config':self.executor.to_config() or {},
        })
        return _dict
    
    @classmethod
    def from_dict(cls, **data):
        return cls(**data)


    # ===========================================
    # Installater / Uninstaller
    # ===========================================

    def install(self, 
                **properties):

        self.installer.__install__(**properties)

    def uninstall(self,
                  **properties):
        
        self.installer.__uninstall__(**properties)


    # ===========================================
    # Load methods
    # ===========================================

    @classmethod
    def load(
            cls, 
            *,
            name:str,
            directory=BLOCK_PATH,
            format='json',
            ntype='prototype',
            installer=INSTALLER.PYTHON,
            **kwargs
        ):

        content, structure = installer.__load__(
            name=name,
            directory=directory,
            format=format,
            ntype=ntype,
            **kwargs
        )
        content.update(**structure)
        
        return cls(**content)




    # ===========================================
    # Execute methods
    # ===========================================
        
    def execute(self, **data):
        
        forward = getattr(self, 'forward', None)

        try:
            exec = self.executor.execute(forward=forward)
            return exec(**data)

        except Exception as e:
            raise PrototypeError(
                f"EXECUTION method failed: {e}", 'EXECUTION')


    def forward(self, name=None, **data):

        print("Executing function in Prototype forward method")
        print(f"Function name: {name}")

        with self.environment as env:

            func   = self.get_register_methods(name=name).call
            print(f"Function to execute: {func}")
            output = func(**data)
        
        return output
    









        