from pydantic import BaseModel, EmailStr

class UserLoginShema(BaseModel): 
    email : EmailStr
    password : str 

class UserSchemaForDump(BaseModel):
    id: int
    email: EmailStr
    group: str
    role: str

    class Config:
        orm_mode = True  # Это позволит использовать объект как источник данных

class JWTSchema(BaseModel):
    jwt : str 

