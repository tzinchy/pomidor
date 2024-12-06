from fastapi import APIRouter, HTTPException, Response, Depends, Request
from models.auth import UserLoginShema
from models.user import UserSchemaForDump
from services.user_service import UserService
from core.httpexceptions import (
    UserNotFoundException,
    InvalidPasswordException,
)
from utils.jwt_utils import create_jwt_token, decode_jwt
from utils.password_utils import get_password_hash


router = APIRouter(prefix="/auth", tags=["Auth % Users"])


@router.post("/register")
async def register_user(user: UserLoginShema):
    """
    Регистрирует нового пользователя. Проверяет, существует ли уже пользователь с таким email.
    """
    try:
        # Хешируем пароль и создаем нового пользователя
        hashed_password = get_password_hash(user.password)
        await UserService.register_user(email=user.email, password=hashed_password)

        # Возвращаем успешный ответ или токен
        return {"message": "User created successfully!"}

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@router.post("/login", description='Иосиф латентный фронтеднре ')
async def login_user(response: Response, user: UserLoginShema, ):
    try:
        print(f"Logging in user: {user.email}")
        is_valid_user = await UserService.validate_user(
            email=user.email, password=user.password
        )
        print(is_valid_user)
        if is_valid_user:
            print("User validated, generating JWT token")
            token = await create_jwt_token(user.email)

            print(f"Generated token: {token}")

            # Set the cookie
            response.set_cookie(
                key="access_token",  
                value=token,          
                httponly=True,       
                max_age=3600          
            )

            return token
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")

    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except InvalidPasswordException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)

    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
@router.post('/test')
async def get_user(request : Request, user : UserSchemaForDump = Depends(decode_jwt)):
    return user