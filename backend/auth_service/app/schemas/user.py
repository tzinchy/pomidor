
from uuid import UUID

from pydantic import BaseModel

class UserUuid(BaseModel):
    user_uuid : UUID

class PasswordSwitch(BaseModel):
    old_password : str 
    new_password : str 

