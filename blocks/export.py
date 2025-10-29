import blocks


#from blocks.engine.execute import _exporter_python_function

from blocks.nodes.node import Node
from blocks.engine.execute import Execute

from blocks.engine.environment import Environment,PYTHON_DEFAULT

#export_function = _exporter_python_function


def task_node(backend='default',
              **backend_args):

    def wrap(function):
        def wrapper(**kwargs):
            
            data_set = {
                'name': 'task_' + str(function.__name__),
                'id': None,
                'version': '0.0.1',
                'path': "",
                '_build': True,
                '_mandatory_attr': False,
                'metadata': {'source': 'Task', 
                            'version': 1.0,
                            'description': ''},
                '_environment': Environment(functions=[function,],
                                            language='python3', 
                                            backend_env=PYTHON_DEFAULT,
                                            build=True,),
                '_executor': Execute(backend=backend, 
                                     **backend_args),}
            
            data_set.update(kwargs)
            return Node(**data_set)
        return wrapper
    return wrap








