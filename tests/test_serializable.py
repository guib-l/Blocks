"""Tests pour le décorateur @serializable"""
import json
import tempfile
from pathlib import Path

from blocks.utils.serializable import serializable, auto_serializable


# Exemple 1 : Classe simple avec @auto_serializable
@auto_serializable
class SimpleClass:
    __slots__ = ('name', 'value', 'count')
    
    def __init__(self, name, value, count=0):
        self.name = name
        self.value = value
        self.count = count


# Exemple 2 : Classe avec paramètres personnalisés
@serializable(exclude_private=True, exclude_attrs=['backend', 'temp'])
class ComplexClass:
    __slots__ = ('name', '_internal', 'backend', 'config', 'temp')
    
    def __init__(self, name, config=None):
        self.name = name
        self._internal = "private data"
        self.backend = lambda x: x * 2  # Non sérialisable
        self.config = config or {}
        self.temp = None


# Exemple 3 : Classe avec objets imbriqués
@auto_serializable
class NestedClass:
    __slots__ = ('parent', 'children')
    
    def __init__(self, parent):
        self.parent = parent
        self.children = []


def test_simple_serialization():
    """Test de sérialisation simple"""
    obj = SimpleClass("test", 42, count=10)
    
    # Test to_dict
    data = obj.to_dict()
    print("to_dict():", data)
    assert data['name'] == "test"
    assert data['value'] == 42
    assert data['count'] == 10
    
    # Test to_json
    json_str = obj.to_json()
    print("to_json():", json_str)
    assert '"name": "test"' in json_str
    
    # Test from_dict
    obj2 = SimpleClass.from_dict(data)
    assert obj2.name == obj.name
    assert obj2.value == obj.value
    
    # Test from_json
    obj3 = SimpleClass.from_json(json_str)
    assert obj3.name == obj.name
    
    print("✓ Test simple serialization passed")


def test_exclusion():
    """Test d'exclusion d'attributs"""
    obj = ComplexClass("test", config={'debug': True})
    
    data = obj.to_dict()
    print("to_dict() with exclusions:", data)
    
    # Les attributs privés ne doivent pas être présents
    assert '_internal' not in data
    assert 'backend' not in data
    assert 'temp' not in data
    
    # Les attributs publics doivent être présents
    assert data['name'] == "test"
    assert data['config'] == {'debug': True}
    
    print("✓ Test exclusion passed")


def test_file_operations():
    """Test de sauvegarde/chargement de fichiers"""
    obj = SimpleClass("file_test", 99, count=5)
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        filepath = f.name
    
    try:
        # Sauvegarder
        obj.save_json(filepath)
        print(f"✓ Saved to {filepath}")
        
        # Charger
        obj2 = SimpleClass.load_json(filepath)
        assert obj2.name == obj.name
        assert obj2.value == obj.value
        assert obj2.count == obj.count
        
        print("✓ Test file operations passed")
    finally:
        Path(filepath).unlink(missing_ok=True)


def test_nested_objects():
    """Test avec objets imbriqués"""
    parent = SimpleClass("parent", 1)
    child = NestedClass(parent)
    child.children = [
        SimpleClass("child1", 10),
        SimpleClass("child2", 20)
    ]
    
    data = child.to_dict()
    print("Nested to_dict():", json.dumps(data, indent=2))
    
    # Le parent doit être sérialisé
    assert 'parent' in data
    
    print("✓ Test nested objects passed")


if __name__ == "__main__":
    print("=" * 60)
    print("Tests du décorateur @serializable")
    print("=" * 60)
    
    test_simple_serialization()
    print()
    
    test_exclusion()
    print()
    
    test_file_operations()
    print()
    
    test_nested_objects()
    print()
    
    print("=" * 60)
    print("✓ Tous les tests sont passés!")
    print("=" * 60)
