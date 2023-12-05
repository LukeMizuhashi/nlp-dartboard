import random
import string
from typing import List
import re
import random

def pick_unique_random_numbers(my_list, n):
    if n > len(my_list):
        raise ValueError("n cannot be greater than the length of the list")

    return random.sample(range(len(my_list)), n)

def validate_n(n):
    """Validates that n is a non-zero, positive integer."""
    if n is None:
        raise ValueError("n must be a non-zero, positive integer.")
    if not isinstance(n, int) or n < 0:
        raise ValueError("n must be a non-zero, positive integer.")

def generate_random_string(length):
    characters = string.ascii_letters + string.digits  # You can add more characters if needed
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string

def get_subset(original_dict: dict, keys_subset: List[str]) -> dict:
    """ Returns a new dict whose keys are in both keys_subset and original_dict and whose values come from original_dict. """
    return {key: original_dict[key] for key in keys_subset if key in original_dict}

def no_op(string: str) -> str:
    return string

def replace_whitespace(string: str) -> str:
    """Replace any run of whitespace with a single space"""
    return re.sub(r'\s+', ' ', string)

def strip_json_structure(json_string: str) -> str:
    """Removes structural JSON characters from the given string"""
    characters_to_remove = '{}[]:,"\''
    for char in characters_to_remove:
        json_string = json_string.replace(char, '')
    return json_string

def fully_minimize_json(json_string: str) -> str:
    """Removes structural JSON characters from the given string and replaces any run of whitespace with a single space"""
    return replace_whitespace(strip_json_structure(json_string))

def partition_string(s: str, overlap: int, chunk_size: int):
    # Initialize the start index and the list to hold the index pairs
    start_index = 0
    index_pairs = []

    # Loop through the string
    while start_index < len(s):
        # Calculate the end index
        end_index = start_index + chunk_size

        # Ensure the end index does not exceed the string length
        end_index = min(end_index, len(s))

        # Append the current start and end index pair to the list
        index_pairs.append([start_index, end_index])

        # Update the start index for the next iteration
        start_index += chunk_size - overlap

        # Handle the case where the overlap is larger than or equal to the chunk size
        if overlap >= chunk_size and start_index < len(s):
            start_index = len(s) - chunk_size

    return index_pairs
