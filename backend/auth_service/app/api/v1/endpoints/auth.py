from fastapi import APIRouter, Response
from depends import user_service
from schemas.auth import UserLogin


router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login_user(user : UserLogin, response : Response):
    payload = await user_service.login_user('dreevxq@gmail.com',None,response)
    
    
    
@router.post("/reset_password")
async def reset_password():
    pass

'''
@router.post("/register")
async def register_user(user: :)
    pass
'''


