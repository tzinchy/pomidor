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
        Validate users by email and password.
        """
        try:
            user = await UserRepository.find_user_by_email(email=email)
            if not user:
                logger.warning(f"User with email {email} not found.")
                raise UserNotFoundException()

            password_from_db = await UserRepository.find_password_by_email(email=email)
            if validate_password(
                provided_password=password, stored_hash=password_from_db
            ):
                logger.info(f"User {email} validated successfully.")
                return True
            else:
                logger.warning(f"Invalid password for user {email}.")
                raise InvalidPasswordException()
        except Exception as e:
            logger.error(f"Error during validation for user {email}: {str(e)}")
            raise e

    @classmethod
    async def register_user(cls, email: EmailStr, password: str):
        """
        Register new user
        """
        existing_user = await UserRepository.find_user_by_email(email=email)
        if existing_user:
            logger.warning(f"User with email {email} already exists.")
            raise UserAlreadyExistsException()

        await UserRepository.create_user(email=email, password=password)
        logger.info(f"User {email} registered successfully.")
        return {"message": "User registered successfully"}

    @classmethod
    async def get_user_data_for_jwt(cls, email: EmailStr):
        """
        Get user data to create JWT (only payload)
        """
        user_data = await UserRepository.all_user_data(email=email)
        print(user_data)
        if not user_data:
            logger.warning(f"User data for JWT not found for email: {email}")
            raise UserNotFoundException(detail="User data not found")
        
        logger.info(f"User data for JWT retrieved for email: {email}")
        return user_data
