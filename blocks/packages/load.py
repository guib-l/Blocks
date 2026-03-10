import os
import sys

import importlib
import importlib.util

from contextlib import contextmanager


@contextmanager
def plugins_env(site_packages: str = None):
    """Context manager to temporarily add a directory to sys.path for plugin loading."""
    original_sys_path = sys.path.copy()
    try:
        if site_packages and site_packages not in sys.path:
            sys.path.insert(0, site_packages)
        yield
    finally:
        sys.path = original_sys_path

def load_plugins(name, path, site_packages=None):
    """Load a plugin module from a specified path, ensuring site-packages is included."""
    with plugins_env(site_packages):
        spec = importlib.util.spec_from_file_location(name, path)
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module

class PluginLoader:
    """Manage dynamic plugin loading with caching and lifecycle management."""
    
    def __init__(self):
        self.plugins = {}
        self.paths = {}  
    
    def load(self, name: str, path: str, site_packages: str = None):
        """Load a plugin or return cached version."""
        if name in self.plugins:
            return self.plugins[name]
        
        module = load_plugins(name, path, site_packages)
        self.plugins[name] = module
        self.paths[name] = (path, site_packages)
        return module
    
    def unload(self, name: str) -> bool:
        """Unload a plugin and remove from cache."""
        if name not in self.plugins:
            return False
        
        if name in sys.modules:
            del sys.modules[name]
        del self.plugins[name]
        self.paths.pop(name, None)
        return True
    
    def reload(self, name: str) -> None:
        """Reload a plugin using stored path information."""
        if name not in self.paths:
            raise ValueError(f"Plugin '{name}' not found or never loaded")
        
        path, site_packages = self.paths[name]
        self.unload(name)
        self.load(name, path, site_packages)
    
    def get_plugin(self, name: str):
        """Retrieve a loaded plugin."""
        return self.plugins.get(name)
    
    def list_plugins(self) -> list:
        """List all loaded plugins."""
        return list(self.plugins.keys())





