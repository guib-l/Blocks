import json
import typing
from functools import wraps


class SerializableEncoder(json.JSONEncoder):
    """Custom JSON encoder for serializable objects."""
    
    def default(self, obj):
        
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        
        if isinstance(obj, set):
            return list(obj)
        
        if isinstance(obj, type):
            return f"{obj.__module__}.{obj.__name__}"
        
        if callable(obj):
            return f"<function {obj.__name__}>"
        
        return super().default(obj)


def auto_serializable(exclude_private=False, 
                      select_attrs= [],
                      exclude_attrs=None, 
                      include_attrs=None,):

    if exclude_attrs is None:
        exclude_attrs = []
    
    def decorator(cls):
                
        def to_dict(self):
            """Convertit l'objet en dictionnaire."""
            data = {}
            
            if select_attrs is not None and len(select_attrs)>0:
                attrs = select_attrs
            elif hasattr(cls, '__slots__'):
                attrs = cls.__slots__
            else:
                attrs = self.__dict__.keys()
            
            for attr in attrs:
                if not hasattr(self, attr):
                    continue

                if attr in exclude_attrs:
                    continue
                if exclude_private and attr.startswith('_'):
                    continue
                if include_attrs is not None and attr not in include_attrs:
                    continue
                
                value = getattr(self, attr)
                
                # Function 'simple'
                if callable(value) and not isinstance(value, type):

                    if isinstance(value, dict):
                        data[attr] = {k: v.__name__ if callable(v) else v 
                                     for k, v in value.items()}
                    else:
                        data[attr] = value.__name__
                # Object avec 'to_dict()'
                elif hasattr(value, 'to_dict'):
                    data[attr] = value.to_dict()
                # Tableau
                elif isinstance(value, (list, tuple)):
                    data[attr] = [
                        v.to_dict() if hasattr(v, 'to_dict') else v 
                        for v in value
                    ]
                # Dictionnaire
                elif isinstance(value, dict):
                    data[attr] = {
                        k: v.to_dict() if hasattr(v, 'to_dict') else v
                        for k, v in value.items()
                    }
                else:
                    try:
                        json.dumps(value)
                        data[attr] = value
                    except (TypeError, ValueError):
                        data[attr] = str(value)
            
            return data
        
        def to_json(self, indent=2, **kwargs):
            """Convertit l'objet en JSON."""
            return json.dumps(
                self.to_dict(), 
                indent=indent, 
                cls=SerializableEncoder,
                **kwargs
            )
        
        def save_json(self, filepath):
            """Sauvegarde l'objet dans un fichier JSON."""
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(self.to_json())
        
        @classmethod
        def from_dict(cls, data):
            """Crée une instance depuis un dictionnaire."""
            return cls(**data)
        
        @classmethod
        def from_json(cls, json_str):
            """Crée une instance depuis une chaîne JSON."""
            data = json.loads(json_str)
            return cls.from_dict(data)
        
        @classmethod
        def load_json(cls, filepath):
            """Charge une instance depuis un fichier JSON."""
            with open(filepath, 'r', encoding='utf-8') as f:
                return cls.from_json(f.read())    
        
        cls.to_dict   = to_dict
        cls.from_dict = from_dict
        cls.to_json   = to_json
        cls.from_json = from_json

        return cls
    return decorator



# Variante simple sans paramètres
def simple_serializable(cls):
    """
    Décorateur simple pour rendre une classe auto-sérialisable.
    Exclut automatiquement les attributs privés et non-sérialisables.
    
    Usage:
        @auto_serializable
        class MyClass:
            __slots__ = ('name', 'value')
            ...
    """
    return auto_serializable()(cls)
