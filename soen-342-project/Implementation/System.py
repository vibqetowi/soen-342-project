import uuid
import bcrypt

def generate_id() -> str:
    """Generates a random UUID for database IDs."""
    return str(uuid.uuid4())  # Return UUID as a string

def hash_password(password: str) -> bytes:
    """Hashes a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(provided_password: str, stored_hashed_password: bytes) -> bool:
    """Checks if the provided password matches the stored hashed password."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hashed_password)