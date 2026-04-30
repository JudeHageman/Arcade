 
import hashlib

def hash_password(password):
    """
    Hashes a plain text password using SHA-256 to match the server's records.
    """
    return hashlib.sha256(password.encode()).hexdigest()