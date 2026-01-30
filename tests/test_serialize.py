import os,sys
import time
import json
from datetime import *
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from dataclasses import dataclass
from configs import *

from tools.serializable import SerializableMixin,Serializable


def _walk(pas=0):
    return pas+1


class Tool(SerializableMixin):
    def __init__(self, name='marteau'):
        self.name = name


class Entity():
    
    def __init__(self, base='human'):
        self.base = base

        self.build = True

    #def __serialize__(self):
    #    return {
    #        'base': self.base
    #    }
        

@Serializable(format='pickle')
class Person(Entity):
    #__slots__ = ('name','age','tool')
    def __init__(self, 
                 name: str, 
                 age: int, 
                 tool: Tool=None,
                 movement=_walk,
                 **kwargs):
        print('__init__ Person')
        super().__init__(**kwargs)

        #self.format = 'pickle'

        self.name = name
        self.age = age
        #self.move = movement

        self.tool = tool

    def build(self,)    :
        print(f'Build person {self.name}, age {self.age}')
        #self.move = self.move(0)
        if self.tool is not None:
            print(f'Has tool : {self.tool.name}')
        else:
            print('No tool')
            




# Utilisation
person = Person("Alice", 30, tool=Tool(name='pelle'))
person.format = 'pickle'
print(person.build)
dict_data = person.to_dict()
print('Serialized Person : ')
print(dict_data)


person_bis = Person.from_dict(dict_data)
print(person_bis.base)
tool = person_bis.tool
print(tool)

person_bis.build
























