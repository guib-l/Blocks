

from blocks.base.prototype import Prototype


from blocks.base.prototype import INSTALLER
from blocks.engine.environment import Environment




def task_node(
        backend    = 'default',
        execute    = None,
        objectType = Prototype,
        **properties):
    """
    Decorator factory that creates a task node wrapper for functions.
    This decorator converts a function into a task node object with metadata,
    configuration, and execution properties. It allows functions to be registered
    as executable tasks within a workflow or processing pipeline.

    Args:
        backend (str, optional): The backend execution environment. Defaults to 'default'.
        execute (callable, optional): Custom execution handler for the task. Defaults to None.
        objectType (type, optional): The class type to instantiate for the node object. 
                                     Defaults to Prototype.
        **properties: Additional properties to be merged into the task node configuration.
    
    Returns:
        callable: A decorator function that wraps the target function and returns
                  an instance of objectType configured as a task node.
    
    Examples:
        >>> @task_node(backend='custom', executor='ProcessPoolExecutor')
        >>> def my_task(data):
        ...    return process(data)
        >>> node = my_task()  # Returns a configured task node object
    
    Notes:
        - The wrapped function becomes a factory that returns a task node instance
        - Default node configuration includes version '0.0.1', Python installer,
          and metadata with source type 'Task'
        - The original function is stored in the 'methods' list of the node
        - Executor and environment settings can be customized via properties
    """ 

    def wrap(function):
        def wrapper_func(**kwargs):
            data_set = {
                'name': str(function.__name__),
                'id': None,
                'version': '0.0.1',
                'mandatory_attr': False,
                'methods':[function,],
                'allowed_name': [function.__name__,],
                'metadata': {'source': 'Task', 
                            'version': 1.0,
                            'description': ''},
                'installer': INSTALLER.PYTHON,
                'installer_config':{
                    'auto':False,
                },
                'environment': Environment,
                'environment_config':{},
                'executor': None,
                'executor_config':{},
            }
            data_set.update(properties)
            
            tmp_node = objectType(**data_set)
            
            return tmp_node
            
        return wrapper_func
    return wrap





def export_function(name='function',
                    inp=None,
                    out=None,
                    execute=False,
                    err="defaults-error"):
    """
    Decorator factory that creates a wrapper for exporting functions with metadata.
    This decorator allows you to wrap a function and attach metadata such as input,
    output, and execution status. It can be used to standardize the way functions are exported or logged within a system.

    Args:
        name (str, optional): The name to associate with the function. Defaults to 'function'.
        inp (any, optional): The input data or parameters for the function. Defaults to None.
        out (any, optional): The expected output or result of the function. Defaults to None.
        execute (bool, optional): Whether to execute the function immediately. Defaults to False.
        err (str, optional): An error message to use if execution fails. Defaults to "defaults-error".
    
    Returns:
        callable: A decorator function that wraps the target function and returns a dictionary
                  containing the function, its type, input, output, and execution results.
    
    Examples:
        >>> @export_function(name='my_function', inp={'x': 1}, out={'result': 2}, execute=True)
        >>> def my_function(x):
        ...     return x + 1
        >>> result = my_function()  # Executes the function and returns metadata

    Notes:
        - The wrapped function can be executed immediately based on the 'execute' flag
        - The returned dictionary includes the original function, its type, input, output, and results
        - Error handling can be customized via the 'err' parameter
    
    """
    def wrap(function):
        def wrapper(**kwargs):
            
            output = {
                'function':function,
                'type':type(function),
                'results':function(**kwargs) if execute else None,
                'input':inp,
                'output':out,
                }

            return output
        return wrapper
    return wrap







