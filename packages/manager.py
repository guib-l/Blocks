import os
import sys
import subprocess
import typing   



class PackageManager:
    def __init__(self, env_path=None):
        self.env_path = env_path


    def enable(self,):
        pass
    def disable(self,):
        pass

    def get_dependencies(self):
        return
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

    def install_dependencies(self, package):
        raise NotImplementedError
    def uninstall_dependencies(self, package):
        raise NotImplementedError
    

    def todict(self,):
        return {}
    def fromdict(self, **kwargs):
        raise NotImplementedError
    










