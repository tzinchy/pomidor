from fastapi import HTTPException
from datetime import timedelta, datetime, timezone
from schema.user import UserSchemaForDump
from config import Settings
from jwt import decode, encode, ExpiredSignatureError, InvalidTokenError

def create_jwt(user: UserSchemaForDump):

    payload = user.model_dump()
    payload['exp'] = datetime.now(timezone.utc) + timedelta(hours=1)

    token = encode(payload, Settings.SECRET_KEY, algorithm=Settings.ALGORITHM)
    
    return token

def decode_jwt(jwt_token: str): 
    try:
        payload = decode(jwt_token, Settings.SECRET_KEY, algorithms=[Settings.ALGORITHM])
        return payload
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token has expired")
    except InvalidTokenError:
        raise HTTPException(status_code=401, detail="Invalid token")

