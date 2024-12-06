import logging
from models.user import EmailStr
from repository.user_repository import UserRepository
from core.httpexceptions import (
    InvalidPasswordException,
    UserNotFoundException,
    UserAlreadyExistsException
)
from utils.password_utils import validate_password


logger = logging.getLogger(__name__)


class UserService:
    @classmethod
    async def validate_user(cls, email: EmailStr, password: str):
        """
        Validates the user's email and password.
        Returns True if the user is valid, raises exceptions otherwise.
        """
        try:
            user = await UserRepository.find_user_by_email(email=email)
            if not user:
                logger.warning(f"User with email {email} not found.")
                raise UserNotFoundException()  # Raise a UserNotFoundException if no user is found

            password_from_db = await UserRepository.find_password_by_email(email=email)
            if validate_password(
                provided_password = password, stored_hash=password_from_db
            ):
                logger.info(f"User {email} validated successfully.")
                return True
            else:
                logger.warning(f"Invalid password for user {email}.")
                raise InvalidPasswordException()  # Raise an exception for invalid password
        except Exception as e:
            logger.error(f"Error during validation for user {email}: {str(e)}")
            raise e

    @classmethod
    async def register_user(cls, email: EmailStr, password: str):
        """
        Registers a new user by checking if the user already exists.
        """
        # Check if the user already exists
        existing_user = await UserRepository.find_user_by_email(email=email)
        if existing_user:
            logger.warning(f"User with email {email} already exists.")
            raise UserAlreadyExistsException()  # Raise exception if user already exists

        # Create the new user
        await UserRepository.create_user(email=email, password=password)
        logger.info(f"User {email} registered successfully.")
        return {"message": "User registered successfully"}
