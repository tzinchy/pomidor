from fastapi import APIRouter, HTTPException, Response, Depends
from models.auth import UserLoginShema
from services.user_service import UserService
from core.httpexceptions import (
    UserNotFoundException,
    InvalidPasswordException,
)
from utils.password_utils import get_password_hash
import logging
from JWTs.JWT_tapo44ek import create_jwt_token, DecodeJWT
from models.user import UserJWTData

deshif_test = DecodeJWT(UserJWTData)

router = APIRouter(prefix="/auth", tags=["Auth % Users"])

logger = logging.getLogger(__name__)

@router.post("/register")
async def register_user(user: UserLoginShema, response : Response):
    """
    Register user and check of existing 
    """
    try:
        # Хешируем пароль и создаем нового пользователя
        hashed_password = get_password_hash(user.password)
        await UserService.register_user(email=user.email, password=hashed_password)

        # Возвращаем успешный ответ или токен
        return {"message": "User created successfully!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", summary="Авторизация пользователя")
async def login_user(response: Response, user: UserLoginShema):
    """
    Logining user and create JWT
    """
    try:
        logger.info(f"Authorization user: {user.email}")
        
        # Проверка валидности пользователя
        is_valid_user = await UserService.validate_user(email=user.email, password=user.password)
        if not is_valid_user:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        
        # Получение данных для JWT
        user_data = await UserService.get_user_data_for_jwt(email=user.email)
        
        # Генерация токена
        token = await create_jwt_token(user_data)
        
        # Установка токена в куки
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=36000,
            secure=True,
        )
        return {"access_token": token}
    except UserNotFoundException as e:
        logger.warning(f"Пользователь не найден: {e.detail}")
        raise HTTPException(status_code=404, detail="User not found")
    except InvalidPasswordException as e:
        logger.warning(f"Неверный пароль для пользователя: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid password")
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
