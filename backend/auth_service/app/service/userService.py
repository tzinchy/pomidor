import logging
from database import pwd_context
from schema.user import EmailStr, UserSchemaForDump
from repository.userRepository import UserRepository
from core.httpexceptions import (
    InvalidPasswordException,
    UserNotFoundException,

)
from fastapi import HTTPException, Request
from datetime import datetime, timedelta, timezone
from app.config import Settings
import jwt


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
            if cls.validate_password(
                password_provided=password, password_from_db=password_from_db
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
    def validate_password(cls, password_provided: str, password_from_db: str) -> bool:
        """
        Verifies the provided password against the stored hashed password.
        """
        return pwd_context.verify(password_provided, password_from_db)

    # В userService.py
    @classmethod
    async def create_jwt_token(cls, email: EmailStr):
        """
        Создание JWT токена для пользователя.
        """
        user_data = await UserRepository.find_user_info_for_jwt(email=email)
        if user_data:
            # Печатаем полученные данные
            logger.info(f"Генерация JWT для пользователя {email} с данными {user_data}")

            # Передаем данные в модель Pydantic
            user_payload = UserSchemaForDump(**user_data)

            # Генерация JWT токена
            jwt_token = UserService.create_jwt(user_payload)
            return jwt_token
        else:
            logger.warning(f"Данные пользователя не найдены для {email}.")
            raise UserNotFoundException()  # Если данные не найдены, генерируем исключение

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

    @classmethod
    def get_password_hash(cls, password: str) -> str:
        """
        Hashes the provided password using bcrypt.
        """
        return pwd_context.hash(password)

    @classmethod
    def create_jwt(cls, user_payload: UserSchemaForDump) -> str:
        payload = user_payload.model_dump()

        payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)

        token = jwt.encode(payload, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)

        return token

    @classmethod
    def decode_jwt(cls, request: Request):
        token = request.cookies.get('access_token')
        print(token)    
        try:
            payload = jwt.decode(
                token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM]
            )
            return payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

    @classmethod
    def get_user(cls, jwt_token : str):
        return cls.decode_jwt(jwt_token)