import os
import sys
import subprocess

import venv
from packages.virtualenv import EnvManager


class CondaEnv(EnvManager):
    
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


