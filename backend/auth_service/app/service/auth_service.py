# app/services/user_service.py
from core.httpexceptions import InvalidPasswordException, UserNotFoundException
from fastapi import HTTPException, Response
from pydantic import EmailStr
from repository.auth_repository import AuthRepository
from schemas.user import UserUuid
from service.auth_email_service import AuthEmailService
from service.jwt_service import create_jwt_token
from utils.password_utils import (
    generate_new_password,
    get_password_hash,
    validate_password,
)


class AuthService:
    def __init__(self, auth_repository : AuthRepository, email_service : AuthEmailService):
        self.auth_repository = auth_repository
        self.email_service = email_service
        
    async def user_exist(self, login_or_email) -> UserUuid | HTTPException:
        if '@' in login_or_email:
            print('this email')
            user_uuid = await self.auth_repository.get_user_uuid_by_email_or_none(login_or_email)
        else:
            print('this login')
            user_uuid = await self.auth_repository.get_user_uuid_by_login_or_none(login_or_email)
        if user_uuid is None: 
            raise UserNotFoundException
        return user_uuid

    def validate_user_districts(self, frontend_payload):
        if frontend_payload['districts'] is not None:
            return True
        return False 
    
    def get_districts(self, frontend_payload):
        return {'districts' : frontend_payload['districts']}
    
    async def login_user(self, login_or_email : str , password: str, response : Response, ) -> UserUuid | HTTPException:
        user_uuid = await self.user_exist(login_or_email=login_or_email)
        print('это uuid', type(user_uuid))
        user_password = await self.auth_repository.get_password_by_uuid(user_uuid=user_uuid)
        user_email = await self.get_email_by_user_uuid(user_uuid=user_uuid)
        if validate_password(provided_password=password, stored_hash=user_password):
            jwt_payload = await self.auth_repository.get_user_backend_payload(user_uuid=user_uuid)
            frontend_payload = await self.auth_repository.get_user_frontend_payload(user_uuid=user_uuid)
            if self.validate_user_districts(frontend_payload):
                districts = self.get_districts(frontend_payload)
                response.set_cookie(
                    key="Districts",
                    value=(create_jwt_token(districts)),
                    httponly=False,
                    max_age=60*60*24*90,
                    samesite="None",
                    secure=True,
                    path='/',
                    domain=".dsa.mlc.gov"  
                )
                response.set_cookie(
                    key="Districts",
                    value=(create_jwt_token(districts)),
                    httponly=False,
                    max_age=60*60*24*90,
                    samesite="None",
                    secure=True,
                    path='/'
                )
            response.set_cookie(
                key="AuthToken",
                value=create_jwt_token(jwt_payload),
                httponly=False,
                max_age=60*60*24*90,
                samesite="None",
                secure=True,
                path='/',
                domain=".dsa.mlc.gov" 
            )
            response.set_cookie(
                key="AuthToken",
                value=create_jwt_token(jwt_payload),
                httponly=False,
                max_age=60*60*24*90,
                samesite="None",
                secure=True,
                path='/'
            )
            response.set_cookie(
                key='Frontend',
                value=create_jwt_token(frontend_payload),
                httponly=False,
                max_age=60*60*24*90,
                samesite="None",
                secure=True,
                path='/',
                domain=".dsa.mlc.gov"  
            )
            response.set_cookie(
                key='Frontend',
                value=create_jwt_token(frontend_payload),
                httponly=False,
                max_age=60*60*24*90,
                samesite="None",
                secure=True,
                path='/'
            )
            response.set_cookie(
                key='uuid',
                value=str(user_uuid),
                httponly=False,
                max_age=60*60*24*90,
                samesite="None",
                secure=True,
                path='/',
                domain=".dsa.mlc.gov" 

            )
            response.set_cookie(
                key='uuid',
                value=user_uuid,
                httponly=False,
                max_age=60*60*24*90,
                samesite="Lax",
                secure=False,
                path='/'  

            )
            return frontend_payload, user_email
        else:
            raise InvalidPasswordException
            
    async def get_email_by_user_uuid(self, user_uuid : str) -> str: 
        result = await self.auth_repository.get_email_by_user_uuid(user_uuid=user_uuid)
        return result

    # async def register_user(self, name: str, email: EmailStr, password: str) -> dict:
    #     pass

    async def reset_password(self, email: EmailStr) -> UserUuid:
        user_uuid = await self.auth_repository.get_user_uuid_by_email_or_none(email=email)
        new_password = generate_new_password()
        email = await self.auth_repository.get_email_by_user_uuid(user_uuid)
        hashed_password = get_password_hash(new_password)
        print(hashed_password)
        result = await self.auth_repository.update_password(user_uuid=user_uuid, hashed_password=hashed_password)
        if result is not None:
            self.email_service.send_password_reset([email], new_password=new_password)
        else:
            raise HTTPException()
        
    async def change_password(self, user_uuid: UserUuid, old_password: str, new_password: str) -> dict:
        password_from_db = await self.auth_repository.get_password_by_uuid(user_uuid=user_uuid)
        if not validate_password(old_password, password_from_db):
            raise HTTPException(status_code=409, detail='Введен неправильный старый пароль!')
        if old_password == new_password: 
            raise HTTPException(status_code=409, detail='Новый и старый пароль совпадают!')

        email = await self.auth_repository.get_email_by_user_uuid(user_uuid)
        hashed_password = get_password_hash(new_password)
        print(hashed_password)
        result = await self.auth_repository.update_password(user_uuid=user_uuid, hashed_password=hashed_password)
        if result is not None:
            self.email_service.send_password_update_notification(recipients=[email])
        else:
            raise HTTPException()
    
    async def create_user(self, first_name, middle_name, last_name, login, email, password, roles_ids, groups_ids, position_ids, districts):
        password =  get_password_hash(password)
        await self.auth_repository.create_user(first_name, middle_name, last_name, login, email, password, roles_ids, groups_ids, position_ids, districts)


    async def get_services(self): 
        await self.auth_repository.get_services()

    async def get_users_fio_list_with_uuid(self):
        return await self.auth_repository.get_users_fio_list_with_uuid()
        
    async def get_user_info_by_uuid(self, user_uuid):
        return await self.auth_repository.get_user_info_by_uuid(user_uuid=user_uuid)
    
    async def get_subordinates_by_uuid(self, user_uuid) -> dict: 
        return await self.auth_repository.get_subordinates_by_uuid(user_uuid=user_uuid)