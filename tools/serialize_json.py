
import json
from pathlib import Path

import pickle



class SerializableEncoder(json.JSONEncoder):
    """Custom JSON encoder for serializable objects."""
    
    def default(self, obj):
        
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        if callable(obj):
            return f"<function {obj.__name__}>"
        
        return super().default(obj)




def serialize_with_json(obj, file_path=None):
    """Serialize an object using JSON."""
    serialized_data = _std_serialize(obj)
    json_data = json.dumps(serialized_data, indent=4, cls=SerializableEncoder)
    
    if file_path:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(json_data)
        return file_path
    
    return json_data

def deserialize_with_json(data_or_path):
    """Deserialize an object using JSON."""
    if isinstance(data_or_path, (str, Path)) and Path(data_or_path).exists():
        with open(data_or_path, 'r', encoding='utf-8') as f:
            json_data = json.load(f)
    else:
        json_data = json.loads(data_or_path)
    
    return _std_deserialize(json_data)


class JsonSerializableMixin:
    """Mixin class for JSON serialization."""
    
    def to_json_file(self, file_path=None):
        """Serialize the object to JSON format."""
        return serialize_with_json(self, file_path)
    
    @classmethod
    def from_json_file(cls, data_or_path):
        """Deserialize an object from JSON format."""
        return deserialize_with_json(data_or_path)







