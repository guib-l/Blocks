import os,sys
from copy import copy, deepcopy
from typing import Any, Dict, TypeVar
from configs import *
from blocks.base.dataset import DataSet

if __name__ == "__main__":
    
    # Create a sample dataset
    data = {
        'name': 'Sample Dataset',
        'values': [1, 2, 3, 4, 5],
        'metadata': {'source': 'generated', 'version': 1.0}
    }
    
    dataset = DataSet(**data)
    
    # Test __getattr__
    print("Testing __getattr__:")
    print("Name:", dataset.name)  # Should print 'Sample Dataset'
    print("Values:", dataset.values)  # Should print [1, 2, 3, 4, 5]
    
    # Test __call__
    print("\nTesting __call__:")
    print("Metadata:", dataset('metadata'))  # Should print {'source': 'generated', 'version': 1.0}
    
    # Test empty_copy
    print("\nTesting empty_copy:")
    empty_dataset = dataset.empty_copy()
    print("Empty Dataset:", empty_dataset.get_dataset())  # Should have same keys but empty values
    
    # Test get_dataset
    print("\nTesting get_dataset:")
    original_data = dataset.get_dataset()
    print("Original Data:", original_data)  # Should match the initial data dictionary
    
    # Test __copy__
    print("\nTesting __copy__:")
    copied_dataset = copy(dataset)
    print("Shallow Copied Dataset:", 
          copied_dataset.get_dataset())  # Should match the original data
    
    # Test __deepcopy__
    print("\nTesting __deepcopy__:")
    deep_copied_dataset = deepcopy(dataset)
    print("Deep Copied Dataset:", 
          deep_copied_dataset.get_dataset())  # Should match the original data

    # Test to_json
    print("\nTesting to_json:")
    json_str = dataset.to_json()
    print("JSON String:", json_str)  # Should print JSON representation of the dataset

    # Test from_json
    print("\nTesting from_json:")
    new_dataset = DataSet.from_json(json_str)
    print("New Dataset from JSON:", new_dataset.get_dataset())  # Should match the original

