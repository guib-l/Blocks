#!/usr/bin/env python3
import os
import sys
import typing
import json
import uuid
import copy

from typing import Dict, Any, TypeVar, Type

class BaseJSONEncoder(json.JSONEncoder):
    
    def default(self, obj: typing.Any) -> typing.Any:
    
        if isinstance(obj, (set,)):
            return list(obj)
        return super().default(obj)


class BaseBlockJSONEncoder(json.JSONEncoder):
    
    def default(self, obj: typing.Any):
    
        if isinstance(obj, obj.__class__):
            try:
                return obj.to_dict()
            except:
                return obj.__str__()
        return super().default(obj)


class NodeJSONEncoder(json.JSONEncoder):

    def default(self, obj: typing.Any) -> typing.Any:
        #print("Encoder : \n",obj,obj.__class__)    
        if isinstance(obj, set):
            return list(obj)
        
        if isinstance(obj, uuid.UUID):
            return str(obj)
        
        if hasattr(obj, "to_dict") and callable(getattr(obj, "to_dict")):
            try:
                return obj.to_dict()
            except Exception:
                return str(obj)
            
        if isinstance(obj, obj.__class__):
            try:
                return obj.to_json()
            except:
                return obj.__str__()
            finally:
                return str(obj)
            
        return super().default(obj)

