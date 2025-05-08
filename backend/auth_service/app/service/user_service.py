# app/services/user_service.py
from core.httpexceptions import UserNotFoundException, InvalidPasswordException
from repository.user_repository import UserRepository
from fastapi import HTTPException
from fastapi import Response
from utils.password_utils import validate_password, generate_new_password, get_password_hash
from repository.user_repository import UserRepository
from service.email_service import EmailService
from schemas.user import UserUuid


class UserService:
    def __init__(self, user_repository : UserRepository, email_service : EmailService):
        self.user_repository = user_repository
        self.email_service = email_service

    async def user_exist(self, login_or_email) -> UserUuid | HTTPException:
        if '@' in login_or_email:
            print('this email')
            user_uuid = await self.user_repository.get_user_uuid_by_email_or_none(login_or_email)
        else:
            print('this login')
            user_uuid = await self.user_repository.get_user_uuid_by_login_or_none(login_or_email)
        if user_uuid is None: 
            raise UserNotFoundException
        return user_uuid

    async def login_user(self, login_or_email : str , password: str, response : Response) -> UserUuid | HTTPException:
        user_uuid = await self.user_exist(login_or_email=login_or_email)
        print('это uuid', type(user_uuid))
        user_password = await self.user_repository.get_password_by_uuid(user_uuid=user_uuid)
        if validate_password(provided_password=password, stored_hash=user_password):
            jwt_payload = self.user_repository.get_user_backend_payload(user_uuid=user_uuid)
            frontend_payload = self.user_repository.get_user_frontend_payload(user_uuid=user_uuid)
            response.set_cookie(
                key="AuthToken",
                value=jwt_payload,
                httponly=False,
                max_age=60*60*24*90,
                samesite="Lax",
                secure=False,
                path='/'
            )
            return frontend_payload
        else:
            raise InvalidPasswordException
            
    async def get_email_by_user_uuid(self, user_uuid : str) -> str: 
        result = await self.user_repository.get_email_by_user_uuid(user_uuid=user_uuid)
        return result

    # async def register_user(self, name: str, email: EmailStr, password: str) -> dict:
    #     pass

    async def reset_password(self, user_uuid: UserUuid) -> UserUuid:
        new_password = generate_new_password()
        email = await self.user_repository.get_email_by_user_uuid(user_uuid)
        self.email_service.send_email_with_new_password(recipients=[email], new_password=new_password)


    # async def get_user_payload(self, email: EmailStr) -> dict | None:
    #     pass
    
    # async def change_password(self, email: EmailStr, old_password: str, new_password: str, confirm_password: str) -> dict:
    #     pass
