import os
import sys
import json

import inspect
from typing import Optional, Any, Callable, Union, Iterable, List
from pathlib import Path
from enum import Enum

from dataclasses import dataclass

from tools.load import (
    PluginLoader,
    save_function_to_file,
)




@dataclass
class MethodObjects:
    name: str = ''
    ftype: Optional[type] = None
    call: Optional[Any] = None
    directory: Optional[str] = None

    def __repr__(self):
        return f'{self.name}:{self.ftype}()'


class Register:

    _default_method_name: Optional[str] = None

    def init_register(
            self,
            allowed_name,
            *,
            files=[],
            methods=[],
            site_packages=None,
        ):
        """Initialize the method register.

        Clears any previous state, loads methods and files, then restricts
        the register to `allowed_name`. Also sets
        :attr:`_default_method_name` to the first registered method so that
        :meth:`get_register_methods` works with ``name=None`` even when
        multiple methods are registered.

        Args:
            allowed_name (list[str]): Whitelist of method names to keep after
                loading. Pass an empty list to allow all discovered methods.
            files (list[str]): Paths to Python files to load as plugins.
                Every top-level function defined in each file is registered.
            methods (list[Callable | str]): Callables or file paths to
                register directly.
            site_packages (str | None): Path to the site-packages directory
                of the virtual environment used to load file-based plugins.
                Forwarded to :class:`PluginLoader` so that dependencies of
                those plugins (e.g. numpy) are resolvable.

        Raises:
            ValueError: If a duplicate method name is encountered while
                loading (``ignore_duplicata=False``).
        """

        self._register_methods = {}
        self._plugin_loader = PluginLoader()
        self._register_site_packages = site_packages

        for _out in [methods, files]:
            self.set_register_methods(_out, ignore_duplicata=False)

        self.registred_files = files
            
        self.allowed_name = allowed_name or list(self._register_methods.keys())  

        self.filter_register_methods(allowed_name=self.allowed_name)
        self._default_method_name = (
            list(self._register_methods.keys())[0]
            if self._register_methods else None
        )

    def set_default_method(self, name: str) -> None:
        """Explicitly set the default method returned when ``name=None``.

        Args:
            name (str): Name of a method already present in the register.

        Raises:
            ValueError: If `name` is not in the register.
        """
        if name not in self._register_methods:
            raise ValueError(
                f"Method '{name}' is not registered in the method registry")
        self._default_method_name = name

    # ===========================================
    # Register of methods
    # ===========================================

    def get_methods(self, name=''):
        """Return the callable stored under `name`.

        Convenience wrapper around :meth:`get_register_methods` that
        returns the raw callable instead of the :class:`MethodObjects`
        container.

        Args:
            name (str): Registered method name.

        Returns:
            Callable: The callable associated with `name`.

        Raises:
            ValueError: If `name` is not in the register.
        """
        func = self.get_register_methods(name=name)
        return func.call

    def get_register_methods(self, name=None):
        """Retrieve a :class:`MethodObjects` entry from the register.

        When `name` is ``None``, :attr:`_default_method_name` is used.
        The default is set automatically to the first registered method
        by :meth:`init_register`, and can be changed with
        :meth:`set_default_method`.

        Args:
            name (str | None): Method name to look up. ``None`` falls back
                to the current default.

        Returns:
            MethodObjects: The register entry containing the callable and
            its metadata.

        Raises:
            ValueError: If `name` (or the default when ``None`` is given)
                is not present in the register.
        """
        if name is None:
            name = self._default_method_name
        if name not in self._register_methods:
            raise ValueError(
                f"Method '{name}' is not registered in the method registry")
        return self._register_methods[name]

    def set_register_methods(self,
                             defaults,
                             name_defaults=None,
                             ignore_decorator=False,
                             ignore_duplicata=True):
        """Register one or more methods into the internal register.

        Accepts a callable, a path to a Python file, or a list of either.
        When a file path is given, every top-level function defined in that
        module is registered (or only `name_defaults` if specified).

        Args:
            defaults (Callable | str | list): The method(s) to register.
                Can be:

                - A callable — registered directly under its ``__name__``.
                - A ``str`` path to a ``.py`` file — functions are loaded
                  via :class:`PluginLoader`.
                - A ``list`` of the above — processed recursively.

            name_defaults (str | None): Override for the registered name,
                or the specific function to extract when loading a file.
            ignore_decorator (bool): Reserved for future use.
            ignore_duplicata (bool): When ``False``, raise :class:`ValueError`
                if a method with the same name is already registered.

        Raises:
            ValueError: If `ignore_duplicata` is ``False`` and the method
                name already exists in the register.
            ValueError: If `name_defaults` is provided for a file path but
                the function is not found in the module.
        """
        # Extract method name first to check for duplicates
        method_name = None
        if isinstance(defaults, Callable) or inspect.isfunction(defaults):
            method_name = defaults.__name__ or name_defaults
        elif isinstance(defaults, str):
            method_name = name_defaults


        if not ignore_duplicata \
                and method_name \
                and method_name in self._register_methods:
            raise ValueError(
                f"Method '{method_name}' is already registered in the method registry")

        if isinstance(defaults, Callable):
            method_obj = MethodObjects()
            method_obj.name = defaults.__name__ or name_defaults or ''
            method_obj.ftype = type(defaults)
            method_obj.call = defaults
            method_obj.directory = None

            self._register_methods[method_obj.name] = method_obj
            return

        if inspect.isfunction(defaults):
            method_obj = MethodObjects()
            method_obj.name = defaults.__name__ or name_defaults or ''
            method_obj.ftype = type(defaults)
            method_obj.call = defaults
            method_obj.directory = None

            self._register_methods[method_obj.name] = method_obj
            return

        if isinstance(defaults, str):
            
            module_name = Path(defaults).stem
            module = self._plugin_loader.load(
                module_name, defaults,
                site_packages=getattr(self, '_register_site_packages', None) or '',
            )

            if name_defaults:
                func = getattr(module, name_defaults, None)
                if func is None:
                    raise ValueError(f"Function '{name_defaults}' not found in {defaults}")
                funcs = [func]
            else:
                funcs = [
                    obj for _, obj in inspect.getmembers(
                        module, inspect.isfunction)
                    if obj.__module__ == module_name
                ]

            for func in funcs:
                method_obj = MethodObjects()
                method_obj.name = func.__name__
                method_obj.ftype = type(func)
                method_obj.call = func
                method_obj.directory = defaults
                self._register_methods[method_obj.name] = method_obj
            return

        if isinstance(defaults, list):
            for method in defaults:
                self.set_register_methods(method)

    def filter_register_methods(self,
                                allowed_name: Optional[List[str]] = None):
        """Remove from the register any method not in `allowed_name`.

        Args:
            allowed_name (list[str] | None): Names to keep. Falls back to
                :attr:`allowed_name` when ``None``.
        """
        if allowed_name is None:
            allowed_name = self.allowed_name

        self._register_methods = {k: v for k, v in self._register_methods.items()
                                  if k in allowed_name}

    def _export(self,
                path,
                method,
                exclude_decorator=None):
        """Write a single method's source code to a file.

        Args:
            path (str): Destination file path.
            method (MethodObjects): Register entry to export.
            exclude_decorator (str | None): Decorator name to strip from
                the source before writing.
        """
        save_function_to_file(
            method.call,
            path,
            exclude_decorator=exclude_decorator or ''
        )

    def export_method(self,
                      filename: Union[str, Iterable] = "",
                      destination: Optional[str] = None,
                      single_file: bool = True,
                      **register):
        """Export registered methods to disk as Python source files.

        Args:
            filename (str | Iterable): Output filename (used when
                `single_file` is ``True``).
            destination (str | None): Target directory. Defaults to the
                current working directory.
            single_file (bool): When ``True``, all methods are appended to
                the same file. Multi-file export is not yet implemented.
            **register: Mapping of ``{name: MethodObjects}`` entries to
                export.

        Raises:
            NotImplementedError: If `single_file` is ``False``.
        """
        if not os.path.isabs(destination or ''):
            destination = os.path.abspath(destination or '.')

        if single_file:
            pathing = os.path.join(destination or '.', str(filename))
            if os.path.exists(pathing):
                os.remove(pathing)

            for _,method in register.items():
                
                self._export(pathing, method, None)

        else:
            raise NotImplementedError(
                'Only Single-file feature is implemented')



    def import_method(self,
                      source: Optional[str] = None,
                      allowed_methods: Optional[list] = None):
        """Load methods from a Python file and add them to the register.

        Args:
            source (str | None): Path to the ``.py`` file to import.
                Resolved to an absolute path if relative.
            allowed_methods (list[str] | None): Whitelist of function names
                to keep after loading. Falls back to :attr:`allowed_name`.

        Raises:
            ValueError: If a function listed in `allowed_methods` is not
                found in the loaded module.
        """
        if not os.path.isabs(source or ''):
            source = os.path.abspath(source or '.')

        self.set_register_methods(source)

        self.filter_register_methods(
            allowed_name=allowed_methods or self.allowed_name)

    def reload_method(self, name: str) -> None:
        """Reload the module that provided `name` from disk.

        Re-reads the source file and refreshes the callable stored in the
        register. Useful when the plugin file has been edited without
        restarting the process.

        Args:
            name (str): Name of a file-backed method to reload.

        Raises:
            ValueError: If `name` is not in the register or was not loaded
                from a file.
        """
        method = self.get_register_methods(name=name)
        if method.directory is None:
            raise ValueError(f"Method '{name}' was not loaded from a file and cannot be reloaded")

        module_name = Path(method.directory).stem
        self._plugin_loader.reload(module_name)

        # Re-register all functions from the reloaded module
        self.set_register_methods(method.directory, ignore_duplicata=True)
        self.filter_register_methods()

    def unload_method(self, name: str) -> bool:
        """Unload the module that provided `name` and remove it from the register.

        All methods that came from the same file are removed together.

        Args:
            name (str): Name of a file-backed method to unload.

        Returns:
            bool: ``True`` when the method was successfully unloaded.

        Raises:
            ValueError: If `name` is not in the register or was not loaded
                from a file.
        """
        method = self.get_register_methods(name=name)
        if method.directory is None:
            raise ValueError(f"Method '{name}' was not loaded from a file and cannot be unloaded")

        module_name = Path(method.directory).stem
        self._plugin_loader.unload(module_name)

        # Remove all methods that came from the same file
        self._register_methods = {
            k: v for k, v in self._register_methods.items()
            if v.directory != method.directory
        }
        return True



