from fastapi import APIRouter
from depends import auth_service
router = APIRouter(prefix='/user') 

@router.get('/get_users')
async def get_users():
    return await auth_service.get_users_fio_list_with_uuid()

@router.get('/get_user/{user_uuid}')
async def get_user(user_uuid : str):
    return await auth_service.get_user_info_by_uuid(user_uuid=user_uuid)