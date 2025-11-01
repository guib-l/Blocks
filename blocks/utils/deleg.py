import os

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




