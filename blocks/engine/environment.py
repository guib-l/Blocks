
from blocks.engine import ENVIRONMENT_TYPE

from blocks.utils.logger import *


from blocks.utils.exceptions import safe_operation
from blocks.utils.exceptions import (ErrorCodeEnv,
                                     EnvironmentError)





class EnvironMixin:


    def __post_init__(self,
                     backend_env=ENVIRONMENT_TYPE.PYTHON,
                     **kwargs):
        env_logger.info('Enter in Environnement Initialization')

        self.env = ENVIRONMENT_TYPE.get(backend_env)

        _backend = backend_env.environment
        self.backend = _backend( **self.env.parameters ) 

        self.env.parameters.update(**kwargs)


    def env_to_dict(self):
        return {
            'backend_env': self.env.__name__,
            'parameters': self.env.parameters,
        }

    # ============================================
    # Variables definition

    @property
    def env(self,):
        return self.__environ__

    @env.setter
    def env(self, new_env):
        self.__environ__ = new_env


    # ============================================
    # Definition Build-in functions

    def __enter__(self):
        try:
            self.open()
            return self
        except:
            env_logger.critical(f'Cannot enter in env')
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_ENTER,
                message="Not closed env.")

    def __exit__(self, exc_type, exc_value, traceback):        
        try:
            self.close()
        except:
            env_logger.critical(f'Env. not cloded')
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_CLOSE,
                message="Not closed env.")

    def __call__(self, _mandat=''):
        env_logger.debug(f'Call {_mandat} method')
        try:
            return getattr(self.backend, _mandat)
        except:
            env_logger.critical(f'Method {_mandat} couldn\'t be called')
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_IMPLEMENT,
                message=f'Method {_mandat} not in object {self.backend.__class__}')
   
    def __diff__(self, other):
        env_logger.debug(f'Check differences with another environment')

        if other == self.env:
            return True
        
        elif other.language == self.env.language:
            if other.environment == self.env.environment:
                return True
        else:
            env_logger.critical(f'Compare only a similar object')
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_DIFF,
                message="Object could not be compare"
            )        
        return False

    def __mix__(self, other):
        # Ajoute les fonctions de 'other' dans self
        # a condition que tout les paramètres soient identiques
        env_logger.critical(f'MIX ENV. IS NOT IMPLEMENTED')
        return NotImplemented


    # ============================================
    # Copy of Environment object

    #def copy(self,):
    #    _env = type(self)(
    #        backend_env=self._backend_env,)
    #    return _env
   
    # ============================================
    # Standard function from Backend attribute

    def open(self):
        env_logger.debug(f'Open environment ')
        return self.__call__("open")()
        
    def close(self,):
        env_logger.debug(f'Close environment ')
        return self.__call__("close")()
    
    def create(self, **kwargs):
        env_logger.debug(f'Create environment ')
        return self.__call__("create")(**kwargs)
    
    def update(self,**kwargs):
        env_logger.debug(f'Update environment ')
        return self.__call__("update")(**kwargs)


class Environment(EnvironMixin):

    __slots__ = (
        'name',
        'language',
        'backend_env',
    )

    def __init__(
            self,
            *,
            name='env',
            language='python3', 
            backend_env=ENVIRONMENT_TYPE.PYTHON,
            **kwargs
        ):
         
        try:
            super().__post_init__(
                backend_env=ENVIRONMENT_TYPE.get(backend_env),
                **kwargs
            )
        except:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_BUILD,
                message="Environment is not properly build"
            )        
        
        self.name = name
        self.language = language

    def __repr__(self):
        return f" (Environment: {self.name} ; Language: {self.language} ; Backend: {self.env.__name__} ) "
    

    def to_config(self):
        return {}
    
    def to_dict(self):

        with safe_operation(
                'Build dict from Environment',
                code=ErrorCodeEnv.ENV_ERROR_SERIALIZATION,
                ERROR=EnvironmentError ):
            
            return {
                'name': self.name,
                'language': self.language,
                'backend_env': self.env.__name__,
                'parameters': self.env.parameters,
            }
    
    @classmethod
    def from_dict(cls, **data: dict):

        with safe_operation(
                'Build Environment from dict',
                code=ErrorCodeEnv.ENV_ERROR_DESERIALIZATION,
                ERROR=EnvironmentError ):

            return cls(
                name=data.get('name', 'env'),
                language=data.get('language', 'python3'),
                backend_env=data.get('backend_env', ENVIRONMENT_TYPE.PYTHON),
                **data.get('parameters', {})
            )















