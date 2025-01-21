from pydantic import BaseModel, EmailStr

class UserLoginShema(BaseModel):
    email: EmailStr
    password: str

class ResetPasswordRequest(BaseModel):
    email: EmailStr