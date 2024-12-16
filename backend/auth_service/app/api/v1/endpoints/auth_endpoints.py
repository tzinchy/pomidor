from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse
from models.auth import UserLoginShema
from services.user_service import UserService
from core.httpexceptions import (
    UserNotFoundException,
    InvalidPasswordException,
)
from utils.password_utils import get_password_hash
import logging
from JWTs import create_jwt_token, DecodeJWT
from models.user import UserJWTData
from pydantic import EmailStr
from core.httpexceptions import EmailSendException

get_user = DecodeJWT(UserJWTData)

router = APIRouter(prefix="/auth", tags=["Auth"])

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
        return {"message": "Login successful"}
    except UserNotFoundException as e:
        logger.warning(f"Пользователь не найден: {e.detail}")
        raise HTTPException(status_code=404, detail="User not found")
    except InvalidPasswordException as e:
        logger.warning(f"Неверный пароль для пользователя: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid password")
    except Exception as e:
        logger.error(f"Ошибка авторизации: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@router.get("/login-form", summary="Тестовая форма для входа", response_class=HTMLResponse)
async def login_form():
    """
    HTML-форма для тестирования редиректа через браузер.
    """
    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Test Login</title>
    <script>
        async function handleLogin(event) {
            event.preventDefault(); // Отключаем стандартную отправку формы

            const email = document.getElementById("email").value;
            const password = document.getElementById("password").value;

            try {
                const response = await fetch("/dgi/auth/login", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ email, password })
                });

                if (response.ok) {
                    window.location.href = "http://127.0.0.1:8001/docs#/";
                } else {
                    const data = await response.json();
                    alert(`Error: ${data.detail || "Login failed"}`);
                }
            } catch (error) {
                console.error("An error occurred during login:", error);
                alert("An error occurred. Please try again.");
            }
        }
    </script>
</head>
<body>
    <h1>Login</h1>
    <form onsubmit="handleLogin(event)">
        <label>Email:</label>
        <input type="email" id="email" value="user@example.com" required><br>
        <label>Password:</label>
        <input type="password" id="password" value="string" required><br>
        <button type="submit">Login</button>
    </form>
</body>
</html>
    """
    return HTMLResponse(content=html_content)

@router.post("/reset_password")
async def reset_password(email: EmailStr):
    """
    Endpoint to reset a user's password.
    """
    try:
        await UserService.reset_password(email=email)
        logger.info(f"Password reset successfully for email: {email}")
        return {"message": "Password reset successfully. Check your email for the new password."}
    except UserNotFoundException as e:
        logger.error(f"Password reset failed: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except EmailSendException as e:
        logger.error(f"Email sending failed: {e.detail}")
        raise HTTPException(status_code=e.status_code, detail=e.detail)
    except Exception as e:
        logger.error(f"Unexpected error during password reset for email {email}: {str(e)}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred. Please try again later.")
    
