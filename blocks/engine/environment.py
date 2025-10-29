import os
import sys
import typing
import abc
import copy

from pathlib import Path

from enum import Enum,Flag


class _default_env:

    def __init__(self,  **kwargs):
        pass
    
    def open(self,):
        print(f'> Open environment "Default"')

    def close(self, **kwargs):
        print(f'> Close environment "Default"')
    
    def create(self, **kwargs):
        print(f'> Create ')

    def update(self, **kwargs):
        print(f'> Update ')




PYTHON_DEFAULT = {
    'env_object':_default_env,
    'functions': [],
}




class _deleguation:
    __deleguation__ = []

class GetDeleguateMixin(_deleguation):

    def __getattribute__(self, name):

        for attr in self.__deleguation__:
            obj = getattr(self, attr, None)
            if obj is not None and hasattr(obj, name):
                return getattr(obj, name)
        raise AttributeError(f"{type(self).__name__} n'a pas d'attribut {name}")
    
class SetDeleguateMixin(_deleguation):

    def __setattr__(self, name, value):

        if name in self.__dict__ or name in getattr(self, '__slot__',()):
            super().__setattr__(name, value)
            return 
        
        for attr in self.__deleguation__:
            obj = getattr(self, attr, None)
            if obj is not None and hasattr(obj, name):
                setattr(obj, name, value)
                return 
            
        super().__setattr__(name, value)



class Environment:


    def __init__(self,
                 name='env',
                 directory='./',
                 language='python3', 
                 backend_env=PYTHON_DEFAULT,
                 build=True,
                 functions=None,
                 **kwargs):
        
        self.name = name
        self.directory = directory


        self.functions = functions
    
        self.language = language

        self._backend_env = backend_env['env_object']
        backend_env.pop('env_object')
        backend_env.update(**kwargs)
        
        if build:  
            self.build(**backend_env)

        self._build = build
            
    @property
    def functions(self, name=None):
        if name is None:
            return self._functions
        else:
            return self._functions[name]
        
    def get_functions(self, index=-1, name=None):
        if name is None:
            name = list(self._functions.keys())[index]
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


    @property
    def language(self):
        return self._lang

    @language.setter
    def language(self, lang):
        self._lang = lang

    @classmethod
    def from_dict(cls, **data):
        return cls(**data)

    def copy(self,):
        return type(self)(
            name=self.name,
            directory=self.directory,
            language=self.language,
            backend_env=self._backend_env,
            build=self._build,
            functions=copy.copy(self.functions),
        )



    def __enter__(self):
        
        self.open()
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        
        try:
            self.close()
        except:
            raise EnvironmentError("Not closed env.")



    def build(self, **kwargs):
        
        self.backend_env = self._backend_env(**kwargs)

    def _base_call(self, _mandat=''):
        try:
            return getattr(self.backend_env, _mandat)
        except:
            raise NotImplemented
        return None
    
   
   
    def open(self):
        value =  self._base_call("open")
        return value()

    def close(self,):
        value = self._base_call("close")
        return value()
    

    def create(self, **kwargs):
        value = self._base_call("create")
        return value(**kwargs)
    
    def update(self,**kwargs):
        value = self._base_call("update")
        return value(**kwargs)




    def __ckeck(self, other):
        # Check si tout les paramètres sont identiques
        return True

    def __add__(self, other):
        # Ajoute les fonctions de 'other' dans self
        # a condition que tout les paramètres soient identiques
        return self




