import blocks

from blocks.base.prototype import Prototype
from blocks.engine.execute import Execute

from blocks.engine.environment import Environment,PYTHON




def task_node(backend    = 'default',
              directory  = '',
              install    = False,
              execute    = None,
              objectType = Prototype,
              **env_args):
    
    if execute is None:
        execute = Execute(backend=backend,
                          build_backend=True)

    def wrap(function):
        def wrapper_func(**kwargs):
            data_set = {
                'name': 'task_' + str(function.__name__),
                'id': None,
                'version': '0.0.1',
                'mandatory_attr': False,
                'codes':[function,],
                'metadata': {'source': 'Task', 
                            'version': 1.0,
                            'description': ''},
                'environment': Environment(language='python3', 
                                           backend_env=PYTHON,
                                           functions=function,
                                           **env_args),
                'executor': execute
            }
            
            if install:
                tmp_node = objectType.install(
                    directory=directory,
                    **data_set
                )
            else:
                tmp_node = objectType(**data_set)
            
            if not kwargs == {}:
                return tmp_node.execute(**kwargs)
            
            return tmp_node
        return wrapper_func
    return wrap


def export_function(name='function',
                    inp=None,
                    out=None,
                    execute=False,
                    err="defaults-error"):

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







