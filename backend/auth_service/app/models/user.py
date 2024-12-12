from pydantic import BaseModel, ConfigDict, EmailStr
from typing import Optional

class UserJWTData(BaseModel):
    user_id: int
    email: EmailStr
    group: Optional[str]  # Сделать поле необязательным
    role: Optional[str]   # Сделать поле необязательным
    exp: int

    model_config = ConfigDict(from_attributes=True)