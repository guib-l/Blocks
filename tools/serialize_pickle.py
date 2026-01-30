
from typing import Any, Callable, TypeVar, Union
from pathlib import Path

import pickle



def serialize_with_pickle(obj, 
                          file_path=None, 
                          protocol=pickle.HIGHEST_PROTOCOL):
    """Serialize an object using pickle."""
    serialized_data = pickle.dumps(obj, 
                                   protocol=protocol)
    
    if file_path:
        with open(file_path, 'wb') as f:
            f.write(serialized_data)
        return file_path
    
    return serialized_data

def deserialize_with_pickle(data_or_path):
    """Deserialize an object using pickle."""
    if isinstance(data_or_path, (str, Path)):
        # If it's a file path
        with open(data_or_path, 'rb') as f:
            return pickle.load(f)
    else:
        # If it's raw bytes
        return pickle.loads(data_or_path)


class PickleSerializableMixin:
    """Mixin class for pickle serialization."""
    
    def to_pickle(self, file_path=None):
        """Serialize the object to pickle format."""
        return serialize_with_pickle(self, file_path)
    
    @classmethod
    def from_pickle(cls, data_or_path):
        """Deserialize an object from pickle format."""
        return deserialize_with_pickle(data_or_path)




