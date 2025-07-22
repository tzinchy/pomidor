from fastapi import APIRouter
from fastapi import Depends
from service.jwt_service import get_user
from schemas.user_token_data import UserTokenData
from depends import auth_service

router = APIRouter(prefix="/user", tags=["User"])


@router.get("/get_users")
async def get_users():
    return await auth_service.get_users_fio_list_with_uuid()


@router.get("/get_user/{user_uuid}")
async def get_user_info(user_uuid: str):
    return await auth_service.get_user_info_by_uuid(user_uuid=user_uuid)


@router.get("/get_subordinates")
async def get_subordinates_by_uuid(user : UserTokenData = Depends(get_user)):
    return await auth_service.get_subordinates_by_uuid(user_uuid=user.user_uuid) 
