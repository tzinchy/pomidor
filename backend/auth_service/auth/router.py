from fastapi import APIRouter, HTTPException, status, Cookie, Response, Depends, Request
from schema.user import UserLoginShema
from service.userService import UserService
from auth.httpexceptions import (
    UserCreationException,
    UserNotFoundException,
    InvalidPasswordException,
)

router = APIRouter(prefix="/auth", tags=["Auth % Users"])


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


@router.post("/login", description='Иосиф латентный фронтеднре ')
async def login_user(response: Response, user: UserLoginShema, ):
    try:
        print(f"Logging in user: {user.email}")
        is_valid_user = await UserService.validate_user(
            email=user.email, password=user.password
        )
        if is_valid_user:
            print("User validated, generating JWT token")
            token = await UserService.create_jwt_token(user.email)

            print(f"Generated token: {token}")

            # Set the cookie
            response.set_cookie(
                key="access_token",  # Cookie key
                value=token,          # JWT token as the value
                httponly=True,        # Prevent access to cookie via JavaScript (important for security)
                secure=True,          # Only send the cookie over HTTPS (important for security)
                samesite="Strict",    # CSRF protection - allow cookie only in same-site requests
                max_age=3600          # Expiration time for the cookie (optional)
            )

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
    

tester = APIRouter(prefix='/test')

@tester.get('/test')
async def test(request: Request, current_user : Depends(UserService.decode_jwt)):
    """
    Test endpoint that requires a valid JWT token to access.
    """
    return {"message": f"Hello, {current_user['email']}"}