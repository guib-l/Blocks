import os
import sys
import subprocess
import typing   



class EnvironMixin:

    __envtype__ = 'EnvironMixin'

    directory: typing.Optional[str] = None
    _exist: bool = False
    
    def __repr__(self):
        return f"EnvironMixin(directory={self.directory}, exists={self.context_exists})"
    
    @property
    def context_exists(self):
        if self.directory is not None and os.path.isdir(self.directory):
            return True
        return self._exist

    @context_exists.setter
    def context_exists(self, trim):
        self._exist = trim

    @property
    def site_packages(self) -> typing.Optional[str]:
        """Path to the site-packages directory of this environment. Override in subclasses."""
        return None

    def enable(self,):
        pass
        
    def disable(self,):
        pass

    def get_context(self):
        return
    
    def diff(self, other):
        return False
    
    def merge(self, other):
        return False


    def install_context(self,):
        raise NotImplementedError
    
    def uninstall_context(self,):
        raise NotImplementedError
    
    def move_context(self,):
        raise NotImplementedError


    def todict(self,):
        return {}
    
    def fromdict(self, **kwargs):
        raise NotImplementedError
    




