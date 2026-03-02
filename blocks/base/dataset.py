#!/usr/bin/env python3
import os
import sys
import typing
import json
import uuid
import copy

from pathlib import Path
from typing import Dict, Any, TypeVar, Union, Type

from tools.encoder import BaseJSONEncoder



T = TypeVar('T', bound='DataSet')

class DataSet:
    """
    Class representing a dataset with various attributes.
    """

    __slots__ = ['_dataset']
    
    def __init__(self, **options: dict):
        """
        Initialize the DataSet with given options.

        Args:
            options (dict): Dictionary to be added to the dataset along with standard elements.
        """
        self._dataset = {}
        for key, value in options.items():
            self.set_option(key, value)

    def resume(self,):
        """
        Return resume of object

        Return 
            Dictionnary
        """
        return self._dataset

    def copy(self):
        """
        Return a copy of the dataset.

        Returns:
            DataSet: A copy of the dataset.
        """
        return DataSet(**self.get_dataset())
    
    def  empty_copy(self):
        """
        Return a copy of the dataset with empty values.

        Returns:
            DataSet: A copy of the dataset with empty values.
        """
        return DataSet(**self.set_empty())
            
    def __check(self) -> bool:
        """
        Check if all elements in the dictionary are not None.

        Returns:
            bool: True if all elements are not None, False otherwise.
        """
        return all(value is not None for value in self._dataset.values())

    def _check_key(self, key: str) -> bool:
        """
        Check if a key exists in the dictionary, case-insensitive.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key.lower() in {k.lower() for k in self._dataset.keys()}
    
    def set_empty(self, empty_values: dict = None) -> dict:
        """
        Set all elements to empty values.
        
        Returns:
            dict: Dictionary with empty values.
        """
        if empty_values is None:
            empty_values = {
                dict: {},
                list: [],
                str: "",
                int: 0,
                float: 0.0
            }
        return {key: empty_values.get(type(val), None) 
                    for key, val in self._dataset.items()}

    def update(self, **kwargs) -> None:
        """
        Update the dataset with new options.
        
        Args:
            kwargs (dict): Dictionary of options to update.
        """
        for key, value in kwargs.items():
            self.set_option(key, value)

    def reset(self) -> None:
        """
        Set all elements except 'atom' and 'weight' to None.
        """
        for key in self._dataset.keys():
            self._dataset[key] = None

    def set_option(self, key: str, obj) -> None:
        """
        Initialize a new element in the dictionary so that it is not None.

        Args:
            name (str): The name of the element.
            obj: The value of the element.

        Raises:
            ValueError: If the name is a method or the element is set to NoneType.
            TypeError: If the name is not a string.
        """
        if not isinstance(key, str):
            raise TypeError(f"Option name must be a string, got {type(name).__name__}")
            
        if callable(getattr(self, key, None)):
            raise ValueError(f"'{key}' est une méthode existante et ne peut pas être utilisé comme attribut")
    
        self._dataset[key] = obj
        setattr(self, key, obj)

    def get_dataset(self, alert: bool = False) -> dict:
        """
        Return the dataset.

        Args:
            alert (bool): If True, print an alert if any element is None.

        Returns:
            dict: The dataset.
        """
        if alert and not self.__check():
            print("[ALERT] :: Some elements are set to 'NoneType'")
        return self._dataset

    def get_attr(self, name: str):
        """
        Return the value of the attribute specified by its name.

        Args:
            name (str): The name of the attribute to retrieve.

        Returns:
            The value of the attribute if it exists.

        Raises:
            AttributeError: If the attribute does not exist.
        """
        if hasattr(self, name):
            return getattr(self, name)
        else:
            raise AttributeError(
                f"L'attribut {name} n'existe pas dans cette dataset.")


    # -----------------------------------------------------
    # Methods for accessing and modifying dataset elements
    # -----------------------------------------------------

    def __call__(self, key: str):
        """
        Return the value associated with the key in the dataset.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            The value associated with the key.
        """
        return self._dataset[key]

    def __getitem__(self, key: str):
        """
        Return the value associated with the key in the dataset.

        Args:
            key (str): The key to retrieve the value for.

        Returns:
            The value associated with the key.
        """
        return self._dataset[key]

    def __setitem__(self, key: str, value):
        """
        Set the value associated with the key in the dataset.

        Args:
            key (str): The key to set the value for.
            value: The value to set.
        """
        self.set_option(key, value)

    def __delitem__(self, key: str):
        """
        Delete the key-value pair from the dataset.

        Args:
            key (str): The key to delete.
        """
        del self._dataset[key]

    def __contains__(self, key: str) -> bool:
        """
        Check if the key exists in the dataset.

        Args:
            key (str): The key to check.

        Returns:
            bool: True if the key exists, False otherwise.
        """
        return key in self._dataset

    def __len__(self) -> int:
        """
        Return the number of elements in the dataset.

        Returns:
            int: The number of elements in the dataset.
        """
        return len(self._dataset)

    def __iter__(self):
        """
        Return an iterator over the keys of the dataset.

        Returns:
            Iterator: An iterator over the keys of the dataset.
        """
        return iter(self._dataset)
    
    
    def __repr__(self) -> str:
        """
        Return a string representation of the dataset.
        Returns:
            str: String representation of the dataset.
        """
        if not self._dataset:
            return f"{self.__class__.__name__}()"
        items = ", ".join(f"{k}={repr(v)}" for k, v in self._dataset.items())
        return f"{self.__class__.__name__}({items})"

    def __getstate__(self) -> Dict[str, Any]:
        """
        Prépare l'état de l'objet pour la sérialisation.
        
        Returns:
            dict: État à sérialiser
        """
        return self._dataset.copy()

    def __setstate__(self, state: Dict[str, Any]) -> None:
        """
        Restaure l'état de l'objet lors de la désérialisation.
        
        Args:
            state (dict): État désérialisé
        """
        self._dataset = {}
        
        for key, value in state.items():
            self.set_option(key, value)

    def __copy__(self) -> T:
        """
        Create a copy of the DataSet instance.

        Returns:
            DataSet: A copy of the DataSet instance.
        """
        return type(self)(**self._dataset.copy())
    
    def __deepcopy__(self, memo: Dict[int, Any]) -> T:
        """
        Create a deep copy of the DataSet instance.

        Args:
            memo (dict): Dictionary to keep track of already copied objects.

        Returns:
            DataSet: A deep copy of the DataSet instance.
        """
        return type(self)(**copy.deepcopy(self._dataset, memo=memo))


    # -----------------------------------------------------
    # JSON Serialization and Deserialization Methods
    # -----------------------------------------------------

    def to_json(self, encoder=BaseJSONEncoder, indent=2):
        """
        Convert the block to a JSON string.
        
        Args:
            encoder (Type[json.JSONEncoder]): The JSON encoder class to use
            indent (int): Number of spaces for indentation
            
        Returns:
            str: A JSON string representation of the block
        """
        return json.dumps(self._dataset.copy(), 
                          cls=encoder, 
                          indent=indent)

    def write_json(self, 
                   directory:str = ".", 
                   json_file:str = 'block.json'):
        """
        Write the block to a JSON file in the specified directory.
        
        Args:
            directory (str): Directory to write the JSON file
            json_file (str): Name of the JSON file
            
        Returns:
            str: Path to the written file
        """
        if not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)
        
        filepath = os.path.join(directory, json_file)
        
        with open(filepath, "w") as fd:
            fd.write(self.to_json())
        
        return filepath

    @classmethod
    def from_json(cls, json_str):
        """
        Create a Block instance from a JSON string.
        
        Args:
            json_str (str): JSON string representation of a Block
            
        Returns:
            Block: A new Block instance
        """
        data = json.loads(json_str)
        return cls(**data)

    @classmethod
    def from_json_file(cls, filepath):
        """
        Create a Block instance from a JSON file.
        
        Args:
            filepath (str): Path to the JSON file
            
        Returns:
            Block: A new Block instance
        """
        with open(filepath, 'r') as f:
            return cls.from_json(f.read())

    def merge(self, other: 'DataSet', overwrite: bool = True) -> T:
        """
        Merge another DataSet into this one.
        
        Args:
            other (DataSet): Another DataSet to merge with this one
            overwrite (bool): If True, values from other will overwrite existing values
                             with the same key. If False, existing values are kept.
                             
        Returns:
            DataSet: Self, after merging
        """
        for key, value in other.get_dataset().items():
            if overwrite or key not in self._dataset:
                self.set_option(key, value)
        return self
        
    @classmethod
    def combine(cls, *datasets: 'DataSet', overwrite: bool = True) -> 'DataSet':
        """
        Combine multiple DataSets into a new one.
        
        Args:
            *datasets: Variable number of DataSet instances to combine
            overwrite (bool): If True, values from later datasets will
                             overwrite values from earlier ones.
                             
        Returns:
            DataSet: A new DataSet containing combined data
        """
        result = cls()
        for dataset in datasets:
            result.merge(dataset, overwrite=overwrite)
        return result
    
    # -----------------------------------------------------
    # Export Methods
    # -----------------------------------------------------

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert the dataset to a dictionary.
        
        Returns:
            dict: A dictionary representation of the dataset
        """
        return self._dataset.copy()
        
    def to_csv(self, filepath: str, delimiter: str = ',') -> str:
        """
        Export the dataset to a CSV file.
        
        Args:
            filepath (str): Path to the output CSV file
            delimiter (str): Delimiter to use in the CSV file
            
        Returns:
            str: Path to the written file
        """
        import csv
        
        # Flatten the dataset for CSV export
        flattened_data = {}
        for key, value in self._dataset.items():
            if isinstance(value, (str, int, float, bool)) or value is None:
                flattened_data[key] = value
            else:
                flattened_data[key] = str(value)
        
        with open(filepath, 'w', newline='') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=flattened_data.keys(), delimiter=delimiter)
            writer.writeheader()
            writer.writerow(flattened_data)
            
        return filepath
        
    def to_yaml(self, filepath: str = None) -> Union[str, str]:
        """
        Convert the dataset to YAML format.
        
        Args:
            filepath (str, optional): If provided, write YAML to this file
            
        Returns:
            str: YAML string or path to written file
        """
        try:
            import yaml
        except ImportError:
            raise ImportError("PyYAML is required for YAML export. Install with 'pip install pyyaml'")
            
        yaml_str = yaml.dump(self._dataset, default_flow_style=False, sort_keys=False)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(yaml_str)
            return filepath
        
        return yaml_str
    
    # -----------------------------------------------------
    # Data Filtering Methods
    # -----------------------------------------------------

    def filter(self, predicate: callable) -> T:
        """
        Create a new DataSet containing only items that satisfy the predicate.
        
        Args:
            predicate: A function that takes a key and value and returns a boolean
            
        Returns:
            DataSet: A new filtered DataSet
        """
        result = type(self)()
        for key, value in self._dataset.items():
            if predicate(key, value):
                result.set_option(key, value)
        return result
        
    def select(self, *keys) -> T:
        """
        Create a new DataSet containing only the specified keys.
        
        Args:
            *keys: Keys to include in the new DataSet
            
        Returns:
            DataSet: A new DataSet with only the selected keys
        """
        result = type(self)()
        for key in keys:
            if key in self._dataset:
                result.set_option(key, self._dataset[key])
        return result
    
    def exclude(self, *keys) -> T:
        """
        Create a new DataSet excluding the specified keys.
        
        Args:
            *keys: Keys to exclude from the new DataSet
            
        Returns:
            DataSet: A new DataSet without the excluded keys
        """
        result = type(self)()
        for key, value in self._dataset.items():
            if key not in keys:
                result.set_option(key, value)
        return result
    
    # -----------------------------------------------------
    # Data Transformation Methods
    # -----------------------------------------------------

    def transform(self, transformer: callable) -> T:
        """
        Create a new DataSet with transformed values.
        
        Args:
            transformer: A function that takes a key and value and returns a new value
            
        Returns:
            DataSet: A new DataSet with transformed values
        """
        result = type(self)()
        for key, value in self._dataset.items():
            result.set_option(key, transformer(key, value))
        return result
        
    def apply(self, func: callable, *keys) -> T:
        """
        Apply a function to specific values in the DataSet.
        
        Args:
            func: A function to apply to each value
            *keys: Keys to apply the function to. If empty, applies to all keys.
            
        Returns:
            DataSet: Self, after applying the function
        """
        target_keys = keys if keys else self._dataset.keys()
        
        for key in target_keys:
            if key in self._dataset:
                self._dataset[key] = func(self._dataset[key])
                setattr(self, key, self._dataset[key])
                
        return self
    
    # -----------------------------------------------------
    # Data Validation Methods
    # -----------------------------------------------------

    def validate(self, schema: Dict[str, Type]) -> bool:
        """
        Validate the dataset against a schema.
        
        Args:
            schema: Dictionary mapping field names to expected types
            
        Returns:
            bool: True if the dataset is valid, False otherwise
        """
        for field, expected_type in schema.items():
            if field not in self._dataset:
                return False
                
            value = self._dataset[field]
            if not isinstance(value, expected_type):
                return False
                
        return True
        
    def assert_valid(self, schema: Dict[str, Type]) -> None:
        """
        Assert that the dataset is valid according to a schema.
        
        Args:
            schema: Dictionary mapping field names to expected types
            
        Raises:
            ValueError: If a required field is missing
            TypeError: If a field has the wrong type
        """
        for field, expected_type in schema.items():
            if field not in self._dataset:
                raise ValueError(f"Required field '{field}' is missing")
                
            value = self._dataset[field]
            if not isinstance(value, expected_type):
                raise TypeError(
                    f"Field '{field}' should be of type {expected_type.__name__}, "
                    f"got {type(value).__name__}"
                )
    
    def is_empty(self) -> bool:
        """
        Check if the dataset is empty.
        
        Returns:
            bool: True if the dataset is empty, False otherwise
        """
        return len(self._dataset) == 0




