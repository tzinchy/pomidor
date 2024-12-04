from fastapi import APIRouter, HTTPException, status, Cookie, Response, Depends
from schema.user import UserLoginShema
from service.userService import UserService
from auth.httpexceptions import UserCreationException, UserNotFoundException, InvalidPasswordException

router = APIRouter(
    prefix='/auth',
    tags=["Auth % Users"]
)

@router.post("/register")
async def register_user(user: UserLoginShema):
    """
    Регистрирует нового пользователя. Проверяет, существует ли уже пользователь с таким email.
    """
    try:
        # Хешируем пароль и создаем нового пользователя
        hashed_password = UserService.get_password_hash(user.password)
        await UserService.register_user(email=user.email, password=hashed_password)

        # Возвращаем успешный ответ или токен
        return {"message": "User created successfully!"}
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
@router.post("/login")
async def login_user(user: UserLoginShema):
    try:
        print(f"Logging in user: {user.email}")
        is_valid_user = await UserService.validate_user(email=user.email, password=user.password)
        if is_valid_user:
            print("User validated, generating JWT token")
            token = await UserService.create_jwt_token(user.email)
            print(f"Generated token: {token}")
            return {"token": token}
        else:
            raise HTTPException(status_code=401, detail="Invalid credentials")
    except UserNotFoundException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except InvalidPasswordException as e:
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        print(f"Unexpected error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

