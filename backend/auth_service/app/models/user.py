from pydantic import BaseModel, ConfigDict, EmailStr

class UserJWTData(BaseModel):
    user_id: int  # Обновлено с id на user_id
    email: EmailStr
    group: str
    role: str
    exp : int

    model_config = ConfigDict(from_attributes=True)
