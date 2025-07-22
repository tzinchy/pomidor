from fastapi import APIRouter, Response, Depends, BackgroundTasks
from depends import auth_service
from schemas.auth import UserLogin, UserResetEmail, CreateUser
from service.jwt_service import get_user, SAD_required, get_fronted_payload, get_user_uuid, get_district_payload
from schemas.user_token_data import UserFrontedPayload, UserTokenData
from schemas.user import PasswordSwitch

router = APIRouter(prefix="/auth", tags=["Auth"])

@router.post("/login")
async def login_user(user : UserLogin, response : Response, background_task : BackgroundTasks) -> dict:
    frontend_payload, user_email = await auth_service.login_user(user.login_or_email,user.password, response)
    #background_task.add_task(auth_email_service.send_login_notification, email=user_email, first_name=frontend_payload['first_name'], middle_name=frontend_payload['middle_name'])
    return {'user' : frontend_payload}
    
    
@router.post("/user/change_password")
async def change_password(password_switch : PasswordSwitch, user : UserTokenData = Depends(get_user)):
    result = await auth_service.change_password(user_uuid=user.user_uuid, old_password=password_switch.old_password, new_password=password_switch.new_password)
    return result

@router.post("/reset_password")
async def reset_password(user_email: UserResetEmail):
    result = await auth_service.reset_password(user_email.email)
    return result

@router.post("/create_user")
async def create_user(create_user : CreateUser, user : UserTokenData = Depends(SAD_required)):
    result = await auth_service.create_user(**create_user.model_dump())
    return result

@router.get('/get_backend_paylod')
async def get_backend_payload(user : UserTokenData = Depends(get_user)):
    return user

@router.get('/get_frontend_payload')
async def get_frontend_payload(user : UserFrontedPayload = Depends(get_fronted_payload)):
    return user

@router.get('/get_uuid')
async def get_uuid(user_uuid = Depends(get_user_uuid)):
    return user_uuid

@router.get('/get_districts')
async def get_districts_payload(districts = Depends(get_district_payload)):
    return districts