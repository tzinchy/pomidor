from pydantic import BaseModel, field_validator, EmailStr
from typing import List, Optional

class UserLogin(BaseModel):
    login_or_email: str
    password: str

    @field_validator('login_or_email')
    @classmethod
    def validate_login_or_email(cls, v: str) -> str:
        # Try to validate as email
        try:
            return EmailStr._validate(v)  # Correct way in Pydantic V2
        except ValueError:
            # If not email, validate as login
            if len(v) < 3:
                raise ValueError("Login must be at least 3 characters")
            return v

class UserRegister(BaseModel):
    email: EmailStr  # This will auto-validate as email
    password: str

class UserResetEmail(BaseModel):
    email : EmailStr

class CreateUser(BaseModel):
    first_name : str
    middle_name : str  
    last_name : str
    login : str
    email : str
    password : str
    districts : Optional[str] = None 
    roles_ids : List[int]
    groups_ids : List[int] 
    position_ids : List[int]