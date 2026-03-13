
from typing import Dict, Optional
from pathlib import Path


from blocks.utils.logger import *

from blocks.utils.exceptions import safe_operation
from blocks.utils.exceptions import (ErrorCodeEnv,
                                     EnvironmentError)

from blocks.packages.load import PluginLoader

from blocks.packages import Packages



class EnvironmentBase:


    def __init__(
            self,
            *,
            name='env',
            language='python3', 
            environment=None, 
            parameters={} ):

        self.name = name
        self.language = language
        self.environment = environment(**parameters) if environment is not None else None
        self.parameters = parameters

    def open(self, **kwds):
        env_logger.debug(f'Open environment ')
        return self.__call__("open")(**kwds)
        
    def close(self, **kwds):
        env_logger.debug(f'Close environment ')
        return self.__call__("close")(**kwds)
    
    def create(self, **kwargs):
        env_logger.debug(f'Create environment ')
        return self.__call__("create")(**kwargs)
    
    def update(self,**kwargs):
        env_logger.debug(f'Update environment ')
        return self.__call__("update")(**kwargs)


    # ============================================
    # Definition Build-in functions

    def __enter__(self, **kwds):
        try:
            self.open(**kwds)            
        except:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_ENTER,
                message="Not closed env.")
        return self

    def __exit__(self, exc_type, exc_value, traceback):        
        try:
            self.close()
        except:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_CLOSE,
                message="Not closed env.")

    def __call__(self, _mandat=''):
        
        try:
            return getattr(self.environment, _mandat)
        except:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_IMPLEMENT,
                message=f'Method {_mandat} not in object {self.environment.__class__}')
   


    # ============================================
    # Variables definition

    @property
    def environment(self,):
        return self.__environ__

    @environment.setter
    def environment(self, new_env):
        self.__environ__ = new_env

    
    def __repr__(self):
        return f" (Environment: {self.name} ; Language: {self.language} ; Type: {self.environment.__class__.__name__} ) "
    
    def to_config(self):
        return self.to_dict()
    
    def to_dict(self):
        
        return {
            'name': self.name,
            'language': self.language,
            'environment': self.environment.__class__,
            'parameters': self.environment.to_dict(),
        }





