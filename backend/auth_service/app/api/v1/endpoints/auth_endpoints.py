from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import HTMLResponse
from models.auth import UserLoginShema
from services.user_service import UserService
from core.httpexceptions import (
    UserNotFoundException,
    InvalidPasswordException
)
from utils.password_utils import get_password_hash
from JWTs import create_jwt_token
from pydantic import EmailStr
import logging
from fastapi import Request
from fastapi.templating import Jinja2Templates
import os

from fastapi import Form

router = APIRouter(prefix="/auth", tags=["Auth"])

logger = logging.getLogger(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "../../../templates")
templates = Jinja2Templates(directory=TEMPLATE_DIR)

@router.get("/login_form", response_class=HTMLResponse)
async def get_login_form(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login"})

@router.get("/register_form", response_class=HTMLResponse)
async def get_register_form(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})

@router.get("/reset_password_form", response_class=HTMLResponse)
async def get_reset_password_form(request: Request):
    return templates.TemplateResponse("reset_password.html", {"request": request, "title": "Reset Password"})

@router.post("/register", response_class=HTMLResponse)
async def register_user(user: UserLoginShema, response: Response):
    """
    Register user and check if it already exists.
    """
    try:
        hashed_password = get_password_hash(user.password)
        await UserService.register_user(email=user.email, password=hashed_password)

        return "<p>User registered successfully!</p>"
    except Exception as e:
        logger.error(f"Error during user registration: {str(e)}")
        return f"<p style='color: red;'>Error: {str(e)}</p>"

@router.post("/login", response_class=HTMLResponse)
async def login_user(user: UserLoginShema, response: Response):
    try:
        is_valid_user = await UserService.validate_user(email=user.email, password=user.password)
        if not is_valid_user:
            return "<p style='color: red;'>Invalid credentials</p>"
        
        user_data = await UserService.get_user_data_for_jwt(email=user.email)
        token = await create_jwt_token(user_data)
        
        response.set_cookie(
            key="access_token",
            value=token,
            httponly=True,
            max_age=3600,
            secure=True
        )
<<<<<<< HEAD
        return {"message": "Login successful"}
    except UserNotFoundException as e:
        logger.warning(f"Пользователь не найден: {e.detail}")
        raise HTTPException(status_code=404, detail="User not found")
    except InvalidPasswordException as e:
        logger.warning(f"Неверный пароль для пользователя: {user.email}")
        raise HTTPException(status_code=401, detail="Invalid password")
=======
        return "<p>Login successful!</p>"
    except UserNotFoundException:
        return "<p style='color: red;'>User not found</p>"
    except InvalidPasswordException:
        return "<p style='color: red;'>Invalid password</p>"
>>>>>>> f787b29 (add frontend table view with tree)
    except Exception as e:
        return f"<p style='color: red;'>Error: {str(e)}</p>"

<<<<<<< HEAD
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
=======
@router.post("/reset_password", response_class=HTMLResponse)
async def reset_password(email: EmailStr = Form(...)):
>>>>>>> f787b29 (add frontend table view with tree)
    try:
        # Ваша логика сброса пароля
        await UserService.reset_password(email=email)
        return "<p class='text-green-500'>Password reset successfully. Check your email for the new password.</p>"
    except UserNotFoundException as e:
        return f"<p class='text-red-500'>Error: {e.detail}</p>"
    except Exception as e:
        return "<p class='text-red-500'>An unexpected error occurred. Please try again later.</p>"