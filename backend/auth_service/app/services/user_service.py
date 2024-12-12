# app/services/user_service.py
import logging
from models.user import EmailStr
from repository.user_repository import UserRepository
from core.httpexceptions import (
    InvalidPasswordException,
    UserNotFoundException,
    UserAlreadyExistsException,
    EmailSendException
)
from utils.password_utils import validate_password, generate_new_password
from utils.email_service import send_email_with_new_password
logger = logging.getLogger(__name__)

from utils.password_utils import validate_password, generate_new_password


class UserService:
    @classmethod
    async def validate_user(cls, email: EmailStr, password: str) -> bool:
        """Validate user credentials."""
        user = await UserRepository.find_user_by_email(email)
        if not user:
            logger.warning(f"User with email {email} not found.")
            raise UserNotFoundException(email)

        password_from_db = await UserRepository.find_password_by_email(email)
        if not validate_password(password, password_from_db):
            logger.warning(f"Invalid password for user {email}.")
            raise InvalidPasswordException(email)

        logger.info(f"User {email} validated successfully.")
        return True

    @classmethod
    async def register_user(cls, email: EmailStr, password: str) -> dict:
        """Register a new user."""
        if await UserRepository.does_user_exist(email):
            logger.warning(f"User with email {email} already exists.")
            raise UserAlreadyExistsException()

        await UserRepository.create_user(email, password)
        logger.info(f"User {email} registered successfully.")
        return {"message": "User registered successfully."}

    @classmethod
    async def reset_password(cls, email: str) -> str:
        """Reset a user's password."""
        user = await UserRepository.find_user_by_email(email)
        if not user:
            logger.warning(f"Password reset requested for nonexistent user {email}.")
            raise UserNotFoundException(email)

        new_password = generate_new_password()
        await UserRepository.update_password(email, new_password)

        try:
            send_email_with_new_password(email, new_password)
        except Exception as e:
            logger.error(f"Failed to send email to {email}: {e}")
            raise EmailSendException()

        logger.info(f"Password reset successfully for user {email}.")
        return new_password

    @classmethod
    async def get_user_data_for_jwt(cls, email: EmailStr) -> dict | None:
        """Get user data for JWT payload."""
        user_data = await UserRepository.find_user_data_for_jwt(email)
        if not user_data:
            logger.warning(f"User data for JWT not found for email: {email}")
            raise UserNotFoundException(email)

        logger.info(f"User data for JWT retrieved for email: {email}")
        return user_data

    @classmethod
    async def change_password(cls, email: EmailStr, old_password: str, new_password: str, confirm_password: str) -> dict:
        """
        Change a user's password after validating the old password.
        """
        if new_password != confirm_password:
            raise InvalidPasswordException(email=email, detail="New password and confirmation do not match.")

        # Validate old password
        user = await UserRepository.find_user_by_email(email)
        if not user:
            raise UserNotFoundException(email=email)

        password_from_db = await UserRepository.find_password_by_email(email)
        if not validate_password(old_password, password_from_db):
            raise InvalidPasswordException(email=email, detail="Old password is incorrect.")

        # Update to new password
        await UserRepository.update_password(email=email, new_password=new_password)
        logger.info(f"Password changed successfully for user {email}.")
        return {"message": "Password changed successfully."}

    @classmethod
    async def change_password(cls, email: EmailStr, old_password: str, new_password: str, confirm_password: str) -> dict:
        """
        Change a user's password after validating the old password and ensuring the new password is not similar to the old one.
        """
        if new_password != confirm_password:
            raise InvalidPasswordException(email=email, detail="New password and confirmation do not match.")

        # Validate old password
        user = await UserRepository.find_user_by_email(email)
        if not user:
            raise UserNotFoundException(email=email)

        password_from_db = await UserRepository.find_password_by_email(email)
        if not validate_password(old_password, password_from_db):
            raise InvalidPasswordException(email=email, detail="Old password is incorrect.")

        # Check if the new password is similar to the old password
        if validate_password(new_password, password_from_db):
            raise InvalidPasswordException(email=email, detail="New password must not be similar to the old password.")

        # Hash and update the new password
        await UserRepository.update_password(email=email, new_password=new_password)
        logger.info(f"Password changed successfully for user {email}.")
        return {"message": "Password changed successfully."}
