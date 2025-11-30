import os
import sys
import typing
import abc
import copy
import json

import inspect
from pathlib import Path

from enum import Enum,Flag

from blocks.engine import PYTHON

from tools.serializable import SerializableMixin

from tools.encoder import EnvJSONEncoder



class Environment(SerializableMixin):

    #__slots__ = (
    #    "name","_functions","_language","_lang",
    #    "_build","backend","_backend_env"
    #)

    def __init__(self,
                 name='env',
                 language='python3', 
                 backend_env=PYTHON,
                 build=True,
                 functions=None,
                 **kwargs):
        
        self.name = name

        self.functions = functions
    
        self.language = language
        self._build = build


        self._backend_env = backend_env
        self.backend      = backend_env.environment

        self._backend_env.parameters.update(**kwargs)
        
        if inspect.isclass(self.backend):
            self.backend = self.backend.sub_build(
                **self._backend_env.parameters
                )  
    
    # ============================================
    # Attributes definition

    @property
    def functions(self, name=None):
        if name is None:
            return self._functions
        else:
            return self._functions[name]
        
    @functions.setter
    def functions(self, defaults=None, **kwfunc):

        if defaults:
            if isinstance(defaults, typing.Callable):
                defaults = {defaults.__name__: defaults}
            elif isinstance(defaults, dict):
                for k,v in defaults.items():
                    if not isinstance(v, typing.Callable):
                        continue
                    defaults[k] = v
            elif isinstance(defaults, typing.List):
                funcs = {}
                for func in defaults:
                    if not isinstance(func, typing.Callable):
                        continue
                    funcs[func.__name__] = func
                defaults = funcs
            else:
                raise TypeError("Defaults must be a callable or a dict.")
            self._functions = defaults
        else:
            self._functions.update(kwfunc)

    def get_functions(self, index=-1, name=None):
        if name is None:
            name = list(self._functions.keys())[index]
        return self._functions[name]


    @property
    def language(self):
        return self._lang

    @language.setter
    def language(self, lang):
        self._lang = lang

    # ============================================
    # Copy of Environment object

    def copy(self, new_name=None):
        return type(self)(
            name=new_name or self.name,
            language=self.language,
            backend_env=self._backend_env,
            build=self._build,
            functions=copy.copy(self.functions),)


    # ============================================
    # Serialization of Environment object

    """
    def __serialize__(self,):
        return dict(
            name=self.name,
            language=self.language,
            backend_env=self._backend_env,
            build=self._build,
            functions=copy.copy(self.functions),)
    """

    """
    @classmethod
    def from_dict(cls, data):
        print('DATA : \n',data)
        return cls(**data)
    
    def to_dict(self,):
        return dict(
            name=self.name,
            language=self.language,
            backend_env=self._backend_env,
            build=self._build,
            functions=copy.copy(self.functions),)

    def to_json(self,):
        return json.dumps(self.to_dict(),
                          indent=4,
                          cls=EnvJSONEncoder)
    
    @classmethod
    def from_json(cls, data):
        data = json.loads(data)
        return cls.from_dict(data)
    """

    # ============================================
    # Definition Build-in functions

    def __enter__(self):
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):        
        try:
            self.close()
        except:
            raise EnvironmentError("Not closed env.")

    def __call__(self, _mandat=''):
        try:
            return getattr(self.backend, _mandat)
        except:
            raise NotImplementedError(
                f'Method {_mandat} not in object {self.backend.__class__}')
   
    def __ckeck(self, other):
        # Check si tout les paramètres sont identiques
        return False

    def __add__(self, other):
        # Ajoute les fonctions de 'other' dans self
        # a condition que tout les paramètres soient identiques

        return self

   
   
    # ============================================
    # Standard function from Backend attribute

    def open(self):
        value =  self.__call__("open")
        return value()

    def close(self,):
        value = self.__call__("close")
        return value()
    
    def create(self, **kwargs):
        value = self.__call__("create")
        return value(**kwargs)
    
    def update(self,**kwargs):
        value = self.__call__("update")
        return value(**kwargs)






