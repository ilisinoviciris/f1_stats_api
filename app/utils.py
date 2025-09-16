import regex

# converts full_name to firstname_lastname (lowercase)
def normalize_driver_id(full_name: str) -> str:
    normalized_id = full_name.strip().lower()
    normalized_id = regex.sub(r"\s+", "_", normalized_id)
    normalized_id = regex.sub(r"[^a-z0-9_]", "", normalized_id)
    return normalized_id
