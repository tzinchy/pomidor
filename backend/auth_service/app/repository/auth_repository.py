from pydantic import EmailStr
from utils.password_utils import get_password_hash
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from sqlalchemy import select
from models.user import User
from fastapi.encoders import jsonable_encoder
from fastapi_cache import FastAPICache

from models.user_backend_payload import UserBackendPayload
from models.user_frontend_payload import UserFrontendPayload
from schemas.user import UserUuid
from sqlalchemy import update


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

    async def create_user(
        self,
        login,
        email,
        password,
        first_name,
        middle_name,
        last_name,
        district_group,
        roles,
        groups,
    ) -> None:
        async with self.db() as session:
            await session.add(User)

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
