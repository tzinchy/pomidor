import jwt
from datetime import datetime, timezone, timedelta
from core.config import Settings
from fastapi import HTTPException, Request 
from repository.user_repository import UserRepository
import logging
from core.httpexceptions import UserNotFoundException
from pydantic import EmailStr
from models.user import UserSchemaForDump
from fastapi import Depends
from services.auth_service import get_token

logger = logging.getLogger(__name__)

async def create_jwt_token(email: EmailStr) -> str:
    """
    Create jwt 
    """
    user_data = await UserRepository.find_user_info_for_jwt(email=email)
    if user_data:

        logger.info(f"Генерация JWT для пользователя {email} с данными {user_data}")

        payload = user_data
        payload["exp"] = datetime.now(timezone.utc) + timedelta(hours=1)

        return jwt.encode(payload, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
    
    else:
        logger.warning(f"Данные пользователя не найдены для {email}.")
        raise UserNotFoundException()  

def decode_jwt(token: str = Depends(get_token)):
    if not token:
        raise HTTPException(status_code=401, detail="Token is missing")

    try:
        payload = jwt.decode(
            token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM]
        )
        
        return payload

    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=401, detail=str(e))