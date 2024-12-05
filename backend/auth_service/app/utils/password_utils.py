from core.config import Settings
import bcrypt

def get_password_hash(password: str) -> str:
    """
    Get password hash.
    Uses the secret key as the salt.
    """
    salt = Settings.SECRET_KEY.encode('utf-8')
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def validate_password(provided_password: str, stored_hash: str) -> bool:
    """
    Validate password
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))
