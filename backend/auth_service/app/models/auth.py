from pydantic import BaseModel, EmailStr

class UserLoginShema(BaseModel):
    email : EmailStr
    password : str