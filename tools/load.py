import os
import sys

import importlib
import importlib.util

import inspect
import ast
import textwrap

from pathlib import Path


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




def _import_modules(file_path: str):
    """
    Import a Python module from a given file path.

    Args:
        file_path (str): Path to the Python file to import
        
    Returns:
        The imported module object
    """

    module_name = Path(file_path).stem
    print(module_name, file_path)
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)

    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module

def _load_function_from_file(file_path: str, 
                             function_name: str=None,
                             ignore_restriction: bool=False):
    """
    Load a function from a Python file.

    Args:
        file_path (str): Path to the Python file
        function_name (str): Name of the function to load (if None, loads the first function found)
        ignore_restriction (bool): If True, allows loading the first function if multiple are found without
                            raising an error; if False, raises an error if multiple functions are found without a specified name

    Returns:
        The loaded function object
    
    Raises:
        ValueError: If no functions are found or if multiple functions are found without specifying a name.
    """

    module = _import_modules(file_path=file_path)

    if function_name is None:
        functions = [obj for name, obj in inspect.getmembers(module) 
                     if inspect.isfunction(obj)]
        if not functions:
            raise ValueError(f"No functions found in the module {module_name}")
        if len(functions) > 1:
            if not ignore_restriction:
                raise ValueError(f"Multiple functions found in the module {module_name}. Please specify a function name.")
            else:
                return functions
        func = functions[0]
    else:
        func = getattr(module, function_name)
    
    return func

def _load_callable_from_file(file_path: str, 
                             callable_name: str=None,
                             ignore_restriction: bool=False):

    module = _import_modules(file_path=file_path)
    
    if callable_name is None:
        callables = [obj for name, obj in inspect.getmembers(module) 
                     if callable(obj)]
        if not callables:
            raise ValueError(f"No callables found in the module {module_name}")
        if len(callables) > 1:
            if not ignore_restriction:
                raise ValueError(f"Multiple callables found in the module {module_name}. Please specify a callable name.")
            else:
                return callables
        callable_obj = callables[0]
    else:
        callable_obj = getattr(module, callable_name)
    
    return callable_obj


def _load_function_with_dependencies(file_path: str, function_name: str=None):

    module = _import_modules(file_path=file_path)
        
    if function_name is None:
        functions = [obj for name, obj in inspect.getmembers(module) 
                     if inspect.isfunction(obj)]
        if not functions:
            raise ValueError(f"No functions found in the module")
        if len(functions) > 1:
            raise ValueError(f"Multiple functions found in the module. Please specify a function name.")
        target_func = functions[0]
    else:
        target_func = getattr(module, function_name)
    
    # Get all functions defined in the module
    module_functions = {name: obj for name, obj in inspect.getmembers(module) 
                       if inspect.isfunction(obj) and obj.__module__ == module.__name__}
    
    # Find dependencies recursively
    dependencies = set()
    
    def find_dependencies(func):
        if func in dependencies:
            return
        dependencies.add(func)
        
        # Get function code and find called functions
        source = inspect.getsource(func)
        for name, obj in module_functions.items():
            if name in source and obj != func:
                find_dependencies(obj)
    
    find_dependencies(target_func)
    
    return list(dependencies)

def _load_function_without_decorators(file_path: str, 
                                      function_name: str = None, 
                                      exclude_decorator: str = None):
    """
    Load a function from a file, optionally removing decorators.
    
    Args:
        file_path: Path to the Python file
        function_name: Name of the function to load (if None, loads the first function)
        exclude_decorator: If specified, only removes this decorator; if None, removes all decorators
        
    Returns:
        The loaded function object without specified decorators
    """
    with open(file_path, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    # Extract imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                          for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            imports.extend(f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                          for alias in node.names)
    
    # Find target function
    target_func_def = None
    for node in tree.body:
        if isinstance(node, ast.FunctionDef):
            if function_name is None or node.name == function_name:
                target_func_def = node
                if function_name:
                    break
    
    if target_func_def is None:
        func_desc = f"'{function_name}'" if function_name else "any function"
        raise ValueError(f"Function {func_desc} not found in {file_path}")
    
    # Extract function source
    func_lines = source.split('\n')
    start_line = target_func_def.lineno - 1
    
    # Find decorator start
    decorator_start = start_line
    for decorator in target_func_def.decorator_list:
        decorator_start = min(decorator_start, decorator.lineno - 1)
    
    # Find function end
    end_line = start_line + 1
    base_indent = len(func_lines[start_line]) - len(func_lines[start_line].lstrip())
    
    for i in range(start_line + 1, len(func_lines)):
        line = func_lines[i]
        if line.strip() and not line.startswith(' ' * (base_indent + 1)) and not line.strip().startswith('#'):
            break
        end_line = i + 1
    
    # Filter decorators
    filtered_lines = []
    
    if exclude_decorator is None:
        # Remove all decorators
        filtered_lines = func_lines[start_line:end_line]
    else:
        # Keep decorators except the excluded one
        for i in range(decorator_start, start_line):
            line = func_lines[i].strip()
            if line.startswith('@'):
                decorator_name = line[1:].split('(')[0].split('.')[0]
                if decorator_name != exclude_decorator:
                    filtered_lines.append(func_lines[i])
            elif line:  # Keep non-empty non-decorator lines
                filtered_lines.append(func_lines[i])
        
        filtered_lines.extend(func_lines[start_line:end_line])
    
    func_source = textwrap.dedent('\n'.join(filtered_lines))
    
    # Execute in temporary namespace
    temp_module = {}
    for import_stmt in imports:
        exec(import_stmt, temp_module)
    exec(func_source, temp_module)
    
    return temp_module[target_func_def.name]







def _write_functions_to_file(output_path: str, 
                             imports: list, 
                             func_sources: list):
    """
    Write imports and function sources to a file.
    
    Args:
        output_path: Path where to save the functions
        imports: List of import statements
        func_sources: List of function source code strings
    """
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    with open(output_path, 'a') as f:
        # Write imports (deduplicated)
        unique_imports = sorted(set(imports))
        if unique_imports:
            f.write('\n'.join(unique_imports))
            f.write('\n\n\n')
        
        # Write function sources
        f.write('\n\n'.join(func_sources))
        f.write('\n')







def _extract_names_from_function_source(func_source: str) -> set:
    """
    Extract all names referenced in a function source code.
    
    Args:
        func_source: Source code of the function as a string
    Returns:
        Set of all names referenced in the function
    """
    names = set()
    try:
        tree = ast.parse(func_source)
        for node in ast.walk(tree):
            if isinstance(node, ast.Name):
                names.add(node.id)
            elif isinstance(node, ast.Attribute):
                # Get the base name (e.g., 'os' from 'os.path')
                base = node
                while isinstance(base, ast.Attribute):
                    base = base.value
                if isinstance(base, ast.Name):
                    names.add(base.id)
    except SyntaxError:
        pass
    
    return names



def _extract_imports_from_source(source: str, required_names: set) -> list:
    """
    Extract only the imports that are actually used in the code.
    
    Args:
        source: Source code to analyze
        required_names: Set of names that are referenced in the code
        
    Returns:
        List of import statements that are actually needed
    """
    tree = ast.parse(source)
    
    # Combine with required_names if provided
    all_required = required_names
    
    necessary_imports = []
    
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                import_name = alias.asname if alias.asname else alias.name
                base_name = alias.name.split('.')[0]
                # Check if the import name or base module is used
                if import_name in all_required or base_name in all_required:
                    stmt = f"import {alias.name}"
                    if alias.asname:
                        stmt += f" as {alias.asname}"
                    necessary_imports.append(stmt)
                    
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            for alias in node.names:
                import_name = alias.asname if alias.asname else alias.name
                # Check if the imported name is actually used
                if import_name in all_required or alias.name == '*':
                    stmt = f"from {module} import {alias.name}"
                    if alias.asname:
                        stmt += f" as {alias.asname}"
                    necessary_imports.append(stmt)

        return necessary_imports



def _get_names_from_functions(func_sources: list) -> set:
    """
    Extract all names referenced in function sources.
    
    Args:
        func_sources: List of function source code strings
        
    Returns:
        Set of all names referenced in the functions
    """
    all_names = set()
    
    for func_source in func_sources:
        try:
            tree = ast.parse(func_source)
            for node in ast.walk(tree):
                if isinstance(node, ast.Name):
                    all_names.add(node.id)
                elif isinstance(node, ast.Attribute):
                    # Get the base name (e.g., 'os' from 'os.path')
                    base = node
                    while isinstance(base, ast.Attribute):
                        base = base.value
                    if isinstance(base, ast.Name):
                        all_names.add(base.id)
        except SyntaxError:
            pass
    
    return all_names


def save_function_to_file(func, 
                          output_path: str, 
                          exclude_decorator: str = None):
    """
    Save a function to a file with all its dependencies and necessary imports.
    
    Args:
        func: The function object to save
        output_path: Path where to save the function
        exclude_decorator: Decorator name to exclude from saved functions
    """
    try:
        source_file = inspect.getfile(func)
    except (TypeError, OSError):
        raise ValueError(f"Cannot determine source file for function {func.__name__}")
    
    with open(source_file, 'r') as f:
        source = f.read()
    
    tree = ast.parse(source)
    
    #valuable_name = _extract_names_from_function_source(inspect.getsource(func))
    #imports = _extract_imports_from_source(source,valuable_name)
    
    # Extract imports
    imports = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.extend(f"import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                        for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ''
            imports.extend(f"from {module} import {alias.name}" + (f" as {alias.asname}" if alias.asname else "")
                          for alias in node.names)
    
    # Get module functions
    module = inspect.getmodule(func)
    module_functions = {name: obj for name, obj in inspect.getmembers(module) 
                       if inspect.isfunction(obj) and obj.__module__ == module.__name__}
    
    # Find dependencies
    dependencies = []
    visited = set()
    
    def find_dependencies(target_func):
        if target_func in visited:
            return
        visited.add(target_func)
        dependencies.append(target_func)
        
        try:
            source_code = inspect.getsource(target_func)
            for name, obj in module_functions.items():
                if name in source_code and obj != target_func and obj not in visited:
                    find_dependencies(obj)
        except (OSError, TypeError):
            pass
    
    find_dependencies(func)
    
    # Extract function definitions
    func_lines = source.split('\n')
    func_sources = []
    func_name_to_node = {node.name: node for node in tree.body if isinstance(node, ast.FunctionDef)}
    
    for dep_func in dependencies:
        node = func_name_to_node.get(dep_func.__name__)
        if not node:
            continue
        
        start_line = node.lineno - 1
        decorator_start = min((d.lineno - 1 for d in node.decorator_list), default=start_line)
        
        # Find function end
        end_line = start_line + 1
        base_indent = len(func_lines[start_line]) - len(func_lines[start_line].lstrip())
        
        for i in range(start_line + 1, len(func_lines)):
            line = func_lines[i]
            if line.strip() and not line.startswith(' ' * (base_indent + 1)) and not line.strip().startswith('#'):
                break
            end_line = i + 1
        
        # Filter decorators
        filtered_lines = []
        
        if exclude_decorator is None:
            filtered_lines = func_lines[start_line:end_line]
        else:
            for i in range(decorator_start, start_line):
                line = func_lines[i].strip()
                if line.startswith('@'):
                    decorator_name = line[1:].split('(')[0].split('.')[0]
                    if decorator_name != exclude_decorator:
                        filtered_lines.append(func_lines[i])
                elif line:
                    filtered_lines.append(func_lines[i])
            
            filtered_lines.extend(func_lines[start_line:end_line])
        
        func_source = textwrap.dedent('\n'.join(filtered_lines))
        func_sources.append(func_source)
    
    _write_functions_to_file(output_path, imports, func_sources)


