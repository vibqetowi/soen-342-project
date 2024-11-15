import uuid

def generate_id() -> str:
    """Generates a random UUID for database IDs."""
    return str(uuid.uuid4())  # Return UUID as a string
