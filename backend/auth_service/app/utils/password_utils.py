from core.config import Settings
import bcrypt

def get_password_hash(password: str) -> str:
    """
    Get password hash.
    bcrypt generates a random salt internally.
    """
    salt = bcrypt.gensalt()  # Генерирует случайную соль
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')

def validate_password(provided_password: str, stored_hash: str) -> bool:
    """
    Validate password.
    Compares provided password with the stored hashed password.
    """
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_hash.encode('utf-8'))

