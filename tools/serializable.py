import functools
import json
import pickle
import inspect
from typing import Any, Callable, TypeVar, Union
from pathlib import Path

import importlib

import datetime
import uuid
import enum

import types

import pickle

from tools.serialize_pickle import PickleSerializableMixin






    

def _std_serialize(obj):
    print('Object : ',obj)

    if isinstance(obj, types.FunctionType):
        return {
            '__function__':obj.__name__,
            '__module__':obj.__module__
        }

    if isinstance(obj, (str, int, float, bool, )):
        print("str,int,... ",obj)
        return str(obj)
    elif isinstance(obj, (Path, type(Path()))):
        return {
            '__type__': 'Path',
            'path': str(obj)
        }
    elif isinstance(obj, (datetime.datetime,datetime.date,datetime.time)):
        return obj.isoformat()
    elif isinstance(obj, uuid.UUID):
        return str(obj)
    elif isinstance(obj, enum.Enum):
        print("Enum",obj)
        return _std_serialize(obj.value)
    elif isinstance(obj, (list, tuple, set)):
        print("list",obj)
        return [_std_serialize(v) for v in obj]
    
    elif isinstance(obj, dict):
        print("dict",obj)
        return {k: _std_serialize(v) for k, v in obj.items()}
    
    elif hasattr(obj, '__slots__'):
        print("__slots__",obj)
        if hasattr(obj,'__serialize__'): 
            attr =  obj.__serialize__()
        else:
            attr = { k: _std_serialize(getattr(obj,k))  for k in obj.__slots__} 
                
        return {'__class__' : obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                'attributes': attr }
    
    elif hasattr(obj, '__dict__'):
        print("__dict__",obj)
        if hasattr(obj,'__serialize__'): 
            attr =  obj.__serialize__()
        else:
            attr = { k: _std_serialize(v)  for k, v in obj.__dict__.items() }
                
        return {'__class__' : obj.__class__.__name__,
                '__module__': obj.__class__.__module__,
                'attributes': attr }
    
    #elif not isinstance(obj,type):
    #    return {'__class__' : obj.__class__.__name__,
    #            '__module__': obj.__class__.__module__,}
    else:
        return str(obj)
    



def _std_deserialize(obj):

    if isinstance(obj,dict):
        # Gérer les types spéciaux
        print(obj)
        if '__type__' in obj:
            if obj['__type__'] == 'Path':
                return Path(obj['path'])
        
        if '__function__' in obj.keys() and '__module__' in obj.keys():
            func_name  = obj['__function__']
            module_name = obj['__module__']

            module = importlib.import_module(module_name)
            return getattr(module, func_name)
        
        if '__class__' in obj.keys() and '__module__' in obj.keys():
            class_name  = obj['__class__']
            module_name = obj['__module__']
            attributes  = obj['attributes']
            
            try:
                module = importlib.import_module(module_name)
                _cls = getattr(module, class_name)
                instance = _cls

            except (ImportError, AttributeError):
                try:
                    _cls = globals()[class_name]
                except:
                    _cls = type(class_name, (), {'__module__': module_name})
                instance = _cls
                    
            if hasattr(obj,'__deserialize__'): 
                deserialized_attrs = obj.__deserialize__()
            else:
                deserialized_attrs = {
                    k: _std_deserialize(v) for k, v in attributes.items() }

            try:
                inst = instance(**deserialized_attrs)
            except:
                inst = instance

            return inst
        else:
            return {k: _std_deserialize(v) for k, v in obj.items()}
        
    elif isinstance(obj, list):
        return [ _std_deserialize(v) for v in obj ]
    else:
        return obj




class NativeSerializableMixin:

    def to_serialize(self):
        return _std_serialize(self)

    def __selector__(self, obj):
        if isinstance(obj, types.FunctionType):
            return {
                '__function__':obj.__name__,
                '__module__':obj.__module__
            }
        if isinstance(obj, types.ModuleType):
            return {}

    def __serilize_dict__(self):
        pass

    def __serialize_std__(self):
        pass

    def __serialize_function(self):
        pass

    def __serialize_class__(self):
        pass





class SerializableMixin(PickleSerializableMixin,
                        NativeSerializableMixin):
    
    __format__ = "pickle"
    
    def __init_subclass__(cls):
        super().__init_subclass__()

        cls.__update_format__(cls)

    def __update_format__(self):
        
        if self.__format__ == "std":
            setattr(self, 'to_dict', self.to_serialize)
            setattr(self, 'from_dict', self.to_deserialize)
            
        if self.__format__ == "pickle":
            setattr(self, 'to_dict', self.to_pickle)
            setattr(self, 'from_dict', self.from_pickle)

    @property
    def format(self):
        return self.__format__

    @format.setter
    def format(self, fmt: str):
        assert fmt in ["pickle", "std"], "Unsupported format"
        self.__format__ = fmt

        self.__update_format__()


def Serializable(format="pickle"):

    def decorator(cls):
        
        class _subSerialize(cls, SerializableMixin):
            __format__ = format

        # Solution trouvée pour conserver le nom de la classe d'origine
        # ainsi que ses metadonnées (essentiel -> solution IA)
        _subSerialize.__name__ = cls.__name__
        _subSerialize.__module__ = cls.__module__
        _subSerialize.__qualname__ = cls.__qualname__
            
        return _subSerialize
    
    return decorator
     









