import blocks

from blocks.nodes.node import Node
from blocks.engine.execute import Execute

from blocks.engine.environment import Environment,PYTHON




def task_node(backend   = 'default',
              directory = '',
              auto      = False,
              install   = False,
              execute   = None,
              **env_args):
    
    if execute is None:
        execute = Execute(backend=backend,
                          build_backend=True)

    def wrap(function):
        def wrapper(**kwargs):
            data_set = {
                'name': 'task_' + str(function.__name__),
                'id': None,
                'version': '0.0.1',
                'path': directory,
                'auto': auto,
                'install': install,
                'mandatory_attr': True,
                'codes':[function,],
                'metadata': {'source': 'Task', 
                            'version': 1.0,
                            'description': ''},
                'environment': Environment(functions=[function,],
                                           language='python3', 
                                           backend_env=PYTHON,
                                           build=True,
                                           **env_args),
                'executor': execute}
            
            tmp_node = Node(**data_set)
            
            if install:
                tmp_node.__install__(
                    directory=directory,
                    **data_set
                )

            if not kwargs == {}:
                return tmp_node.execute(**kwargs)
            
            return tmp_node
        return wrapper
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







