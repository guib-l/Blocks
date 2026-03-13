import os
from typing import *




class Transformer:

    def __init__(
            self,
            additional_parameters: Optional[Dict[str, Any]] = None,
            rename_attr = None,
            modify_attr = None,
            ignore_attr = None, ):
        
        self.ra = rename_attr
        self.ma = modify_attr
        self.ia = ignore_attr
        self.ap = additional_parameters

    def _rename(self, data):
        for old_name, new_name in self.ra or []:
            if old_name in data:
                data[new_name] = data.pop(old_name)
        return data
    
    def _modify(self, data):
        for name, new_value in self.ma or []:
            if name in data:
                data[name] = new_value
        return data
    
    def _ignore(self, data):
        for name in self.ia or []:
            if name in data:
                data.pop(name)
        return data

    def to_config(self,):
        return {            
            'rename_attr':self.ra,
            'modify_attr':self.ma,
            'ignore_attr':self.ia,
        }

    def __call__(self, input):

        input = {**input, **(self.ap or {})}

        out = self._rename(input)
        out = self._modify(out)
        output = self._ignore(out)
        
        return output




