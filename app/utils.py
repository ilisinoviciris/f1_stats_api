import regex

def normalize_driver_id(full_name: str) -> str:
    """
    Convert driver full_name to firstname_last_name (all lowercase) to use as driver_id.
    For example: 'Charles LECLERC' -> 'charles_leclerc'
    """
    normalized_id = full_name.strip().lower()
    normalized_id = regex.sub(r"\s+", "_", normalized_id)
    normalized_id = regex.sub(r"[^a-z0-9_]", "", normalized_id)
    return normalized_id

def normalize_full_name(full_name: str) -> str:
    """
    Convert driver full_name so that:
    - remove extra spaces
    - every first letter of every word in a string is capitalized
    - all other letters are lowercase unless:
        - if there's an apostrophe "'" in a string capitalize first letter after it
    For example: 'Patricio O'WARD' -> 'Patricio O'Ward'. 
    """
    normalized_full_name = regex.sub(r"\s+", " ", full_name.strip().lower())
    normalized_full_name = regex.sub(r"(^|\s|')([a-z])", lambda m: m.group(1) + m.group(2).upper(), normalized_full_name)

    return normalized_full_name