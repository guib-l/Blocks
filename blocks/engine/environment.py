
from typing import Dict, Optional
from pathlib import Path

from blocks.engine import ENVIRONMENT_TYPE

from blocks.utils.logger import *

from blocks.utils.exceptions import safe_operation
from blocks.utils.exceptions import (ErrorCodeEnv,
                                     EnvironmentError)

from tools.load import PluginLoader





class EnvironMixin:


    def __post_init__(self,
                     backend_env=ENVIRONMENT_TYPE.PYTHON,
                     **kwargs):
        env_logger.info('Enter in Environnement Initialization')

        self.env = ENVIRONMENT_TYPE.get(backend_env)

        _backend = backend_env.environment
        self.backend = _backend( **self.env.parameters ) 

        self.env.parameters.update(**kwargs)
        print('Environment parameters : ',self.env.parameters)

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
        except:
            env_logger.critical(f'Cannot enter in env')
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR_ENTER,
                message="Not closed env.")
        return self

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

#    __slots__ = (
#        'name',
#        'language',
#        'backend_env',
#    )

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



class EnvironmentPluginManager:

    def __init__(self):
        self._env_registry: Dict[str, 'Environment'] = {}
        self._active_name: Optional[str] = None
        self._plugin_loader = PluginLoader()

    # ------------------------------------------------------------------
    # Registration
    # ------------------------------------------------------------------

    def register(self, name: str, env: 'Environment') -> None:
        """Register an already-built :class:`Environment` under *name*.
        """
        env_logger.debug(f'PluginManager: register environment "{name}"')
        self._env_registry[name] = env

    def unregister(self, name: str) -> bool:
        """Remove environment *name* from the registry.
        """
        if name not in self._env_registry:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR,
                message=f"Environment '{name}' is not registered"
            )
        if self._active_name == name:
            self._active_name = None
        del self._env_registry[name]
        env_logger.debug(f'PluginManager: unregistered environment "{name}"')
        return True

    # ------------------------------------------------------------------
    # Factory helpers
    # ------------------------------------------------------------------

    def load_env(self, name: str, env_class: type, **kwargs) -> 'Environment':
        """Instantiate *env_class* with *kwargs*, then register it as *name*.
        """
        env_logger.debug(f'PluginManager: load_env "{name}" from {env_class}')
        env = env_class(**kwargs)
        self.register(name, env)
        return env

    def load_env_from_file(
            self,
            name: str,
            path: str,
            class_name: str,
            **kwargs
        ) -> 'Environment':
        """Load a backend class from a plugin file, then register it as *name*.
        """
        with safe_operation(
                f'load env from file {path}',
                code=ErrorCodeEnv.ENV_ERROR_BUILD,
                ERROR=EnvironmentError):

            module_name = Path(path).stem
            module      = self._plugin_loader.load(module_name, path)
            env_class   = getattr(module, class_name)

        env_logger.debug(
            f'PluginManager: load_env_from_file "{name}" '
            f'← {class_name} @ {path}'
        )
        return self.load_env(name, env_class, **kwargs)

    # ------------------------------------------------------------------
    # Activation
    # ------------------------------------------------------------------

    def switch(self, name: str) -> None:
        """Set *name* as the active environment.
        """
        if name not in self._env_registry:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR,
                message=f"Cannot switch: environment '{name}' is not registered"
            )
        self._active_name = name
        env_logger.info(f'PluginManager: active environment → "{name}"')

    @property
    def active(self) -> 'Environment':
        """Return the currently active :class:`Environment`.

        Raises:
            EnvironmentError: If no environment is active.
        """
        if self._active_name is None or self._active_name not in self._env_registry:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR,
                message="No active environment set in PluginManager"
            )
        return self._env_registry[self._active_name]

    # ------------------------------------------------------------------
    # Hot-reload / unload
    # ------------------------------------------------------------------

    def reload_env(self, name: str) -> None:
        """Reload the plugin module that backs *name* and re-register it.
        """
        env = self._env_registry.get(name)
        if env is None:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR,
                message=f"reload_env: '{name}' is not registered"
            )

        source_file = getattr(env, '_plugin_source_file', None)
        if source_file is None:
            raise EnvironmentError(
                code=ErrorCodeEnv.ENV_ERROR,
                message=f"reload_env: '{name}' was not loaded from a file"
            )

        class_name = type(env.backend).__name__
        env_logger.info(f'PluginManager: reload_env "{name}"')
        module_name = Path(source_file).stem
        self._plugin_loader.reload(module_name)
        module    = self._plugin_loader.get_plugin(module_name)
        env_class = getattr(module, class_name)
        new_env   = env_class(**getattr(env, '_plugin_kwargs', {}))
        self._env_registry[name] = new_env

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------

    def list_envs(self) -> list:
        """Return the list of registered environment names."""
        return list(self._env_registry.keys())

    def __contains__(self, name: str) -> bool:
        return name in self._env_registry

    def __repr__(self) -> str:
        active = self._active_name or 'None'
        return (
            f"EnvironmentPluginManager("
            f"active='{active}', "
            f"registered={self.list_envs()})"
        )


# ---------------------------------------------------------------------------


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
        self.environment = environment(**parameters)
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
        return f" (Environment: {self.name} ; Language: {self.language} ; Type: {self.environment.__name__} ) "
    
    def to_config(self):
        return {}
    
    def to_dict(self):

        return {
                'name': self.name,
                'language': self.language,
                'environment': self.environment,
                'parameters': self.environment.parameters,
        }


from packages.package import Packages

class pyEnvironment(Packages):

    def __init__(self, **kwargs):
        super().__init__(
            directory=kwargs.get('directory', '.'),
            env_name=kwargs.get('env_name', 'pip-venv.01'),
            env_type=kwargs.get('env_type', 'venv'),
            mng_type=kwargs.get('mng_type', 'pip'),
            dependencies=kwargs.get('dependencies', []),
            auto_build=kwargs.get('auto_build', True),
        )

    def open(self, **kwds):
        env_logger.debug(f'Open Python environment ')
        self.activate()
        
    def close(self, **kwds):
        env_logger.debug(f'Close Python environment ')
        self.deactivate()







