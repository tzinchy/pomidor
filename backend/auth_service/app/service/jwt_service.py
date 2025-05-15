import os
from datetime import datetime, timedelta, timezone
from typing import Type, Optional, List
import jwt
from dotenv import load_dotenv
from fastapi import Depends, HTTPException, Request, status
from pydantic import BaseModel 

from schemas.user_token_data import UserTokenData

load_dotenv()

ALGORITHM = os.getenv("ALGORITHM", "HS256")
SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY must be set in environment variables")


def create_jwt_token(payload: dict) -> str:
    """Создание JWT токена"""
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Payload cannot be empty"
        )
    
    payload = payload.copy()
    payload["exp"] = int((datetime.now(timezone.utc) + timedelta(days=90)).timestamp())
    return jwt.encode(payload, SECRET_KEY, ALGORITHM)

def get_token(request: Request) -> str:
    """Извлечение токена из куки AuthToken"""
    token = request.cookies.get("AuthToken")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication token missing"
        )
    return token

class AuthChecker:
    def __init__(
        self,
        response_model: Type[BaseModel] = UserTokenData,
        required_roles: Optional[List[int]] = None,
        required_groups: Optional[List[int]] = None,
        required_positions: Optional[List[int]] = None
    ):
        self.response_model = response_model
        self.required_roles = required_roles or []
        self.required_groups = required_groups or []
        self.required_positions = required_positions or []

    def __call__(self, token: str = Depends(get_token)) -> UserTokenData:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            user_data = self.response_model(**payload)
            
            # Проверка ролей
            if self.required_roles and not any(role in user_data.roles_ids for role in self.required_roles):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient role privileges"
                )
                
            # Проверка групп
            if self.required_groups and not any(group in user_data.groups_ids for group in self.required_groups):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient group privileges"
                )
                
            # Проверка позиций
            if self.required_positions and not any(pos in user_data.positions_ids for pos in self.required_positions):
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient position privileges"
                )
            
            return user_data

        except jwt.ExpiredSignatureError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired"
            )
        except jwt.InvalidTokenError:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=str(e)
            )
        
async def get_user(token: str = Depends(get_token)) -> UserTokenData:
    """Базовая зависимость для получения данных пользователя без проверок прав"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return UserTokenData(**payload)
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}"
        )
    
# Специализированные проверки
class GetMpAdmin(AuthChecker):
    def __init__(self):
        super().__init__(required_roles=[1])  # Пример: роль 1 для админа

class GetHrAdmin(AuthChecker):
    def __init__(self):
        super().__init__(required_roles=[2])  # Пример: роль 2 для HR-админа

class GetHrUser(AuthChecker):
    def __init__(self):
        super().__init__(required_roles=[3])  # Пример: роль 3 для HR-пользователя

class GetHrCandidate(AuthChecker):
    def __init__(self):
        super().__init__(required_roles=[4])  # Пример: роль 4 для кандидата

def SAD_required():
    return AuthChecker(required_groups=[5,6])
    
def admin_required():
    return AuthChecker(required_roles=[1], required_groups=[1])

def hr_manager_required():
    return AuthChecker(required_roles=[2, 3], required_positions=[10])