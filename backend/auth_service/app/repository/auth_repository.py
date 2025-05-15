from pydantic import EmailStr
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, text
from models.user import User

from models.user_backend_payload import UserBackendPayload
from models.user_frontend_payload import UserFrontendPayload
from schemas.user import UserUuid
from sqlalchemy import update
import json
from typing import List, Optional


class AuthRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_user_uuid_by_email_or_none(self, email: EmailStr) -> UserUuid | None:
        async with self.db() as session:
            print("validate user by email")
            query_result = await session.execute(
                select(User.user_uuid).where(User.email == email)
            )
            result = query_result.scalar_one_or_none()
            return result

    async def get_user_uuid_by_login_or_none(self, login: str) -> UserUuid | None:
        async with self.db() as session:
            print("validate user by login")
            query_result = await session.execute(
                select(User.user_uuid).where(User.login == login)
            )
            result = query_result.scalar_one_or_none()
            return result

    async def get_password_by_uuid(self, user_uuid: str) -> str:
        async with self.db() as session:
            query_result = await session.execute(
                select(User.password).where(User.user_uuid == user_uuid)
            )
            result = (
                query_result.scalar_one()
            )  
            return result

    async def get_email_by_user_uuid(self, user_uuid: str) -> EmailStr:
        async with self.db() as session:
            query_result = await session.execute(
                select(User.email).where(User.user_uuid == user_uuid)
            )
            result = query_result.scalar_one_or_none()
            print(result)
            return result

    async def create_candidate_user():
        pass

    async def update_password(self, user_uuid: str, hashed_password: str) -> str | None:
        async with self.db() as session:
            query_result = await session.execute(
                update(User)
                .where(User.user_uuid == user_uuid)
                .values(password=hashed_password)
                .returning(User.user_uuid)
            )
            result = query_result.scalar_one_or_none()
            await session.commit()
            return result

    async def get_user_backend_payload(self, user_uuid):
        async with self.db() as session:
            query_result = await session.execute(
                select(UserBackendPayload).where(user_uuid == user_uuid)
            )
            result = query_result.scalars().first()
            return result.as_dict()

    async def get_user_frontend_payload(self, user_uuid):
        async with self.db() as session:
            print(type(user_uuid))
            query_result = await session.execute(
                select(
                    UserFrontendPayload.first_name,
                    UserFrontendPayload.middle_name,
                    UserFrontendPayload.last_name,
                    UserFrontendPayload.positions_info,
                    UserFrontendPayload.districts,
                    UserFrontendPayload.roles,
                    UserFrontendPayload.groups_info,
                ).where(UserFrontendPayload.user_uuid == user_uuid)
            )
            result = [dict(row) for row in query_result.mappings().all()][0]
            return result
        
    async def create_user(
        self,
        first_name: str,
        middle_name: str,
        last_name: str,
        login: str,
        email: str,
        password: str,
        roles_ids: List[int],
        groups_ids: List[int],
        position_ids: List[int],
        district_group_id: Optional[int] = None,
    ):
        async with self.db() as session:
            query = text("""
                INSERT INTO auth.user 
                (first_name, middle_name, last_name, login, email, password, 
                roles_ids, groups_ids, positions_ids, district_group_id) 
                VALUES (:first_name, :middle_name, :last_name, :login, :email, :password, 
                        :roles_ids, :groups_ids, :positions_ids, :district_group_id)
            """)
            params = {
                "first_name": first_name,
                "middle_name": middle_name,
                "last_name": last_name,
                "login": login,
                "email": email,
                "password": password,
                "roles_ids": roles_ids,  # Просто передаём список Python
                "groups_ids": groups_ids,
                "positions_ids": position_ids,
                "district_group_id": district_group_id,
            }
            await session.execute(query, params)
            await session.commit()
    
    async def get_services(self):
        async with self.db() as session:
            query_result = await session.execute(text('''select service_id, service from auth.service'''))
            return [dict(row) for row in query_result.mappings().all()][0]