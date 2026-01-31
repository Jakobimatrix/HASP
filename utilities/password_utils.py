# db/password_utils.py
import hashlib
import secrets

def generate_salt(length: int = 16) -> str:
    """
    Generate a cryptographically secure random salt.
    Default is 16 bytes, returned as hex string.
    """
    return secrets.token_hex(length)

def hash_password(salt: str, password: str) -> str:
    """
    Hash a password with a given salt using SHA-256.
    Returns hex digest string.
    """
    return hashlib.sha256((salt + password).encode()).hexdigest()

def verify_password(stored_hash: str, salt: str, password_attempt: str) -> bool:
    """
    Verify if a password attempt matches the stored hash using the stored salt.
    """
    return hash_password(salt, password_attempt) == stored_hash
