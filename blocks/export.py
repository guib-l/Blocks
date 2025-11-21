import blocks

from blocks.nodes.node import Node
from blocks.engine.execute import Execute

from blocks.engine.environment import Environment,PYTHON




def task_node(backend='default',
              **backend_args):

    def wrap(function):
        def wrapper(**kwargs):
            data_set = {
                'name': 'task_' + str(function.__name__),
                'id': None,
                'version': '0.0.1',
                'path': "",
                '_build': False,
                '_mandatory_attr': False,
                'metadata': {'source': 'Task', 
                            'version': 1.0,
                            'description': ''},
                '_environment': Environment(functions=[function,],
                                            language='python3', 
                                            backend_env=PYTHON,
                                            build=True,),
                '_executor': Execute(backend=backend, 
                                     **backend_args),}
            
            if not kwargs == {}:
                return Node(**data_set).execute(**kwargs)
            
            return Node(**data_set)
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







