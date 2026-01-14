

from blocks.base.prototype import Prototype


from blocks.base.prototype import INSTALLER
from blocks.engine.environment import Environment




def task_node(backend    = 'default',
              execute    = None,
              objectType = Prototype,
              **properties):
    
    

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







