import random
import string
from typing import List

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