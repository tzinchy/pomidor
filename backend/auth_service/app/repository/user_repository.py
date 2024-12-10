from repository.database import async_session_maker
from pydantic import EmailStr
from sqlalchemy import text
from core.config import Settings
from core.httpexceptions import UserNotFoundException
from models.user import UserJWTData

class UserRepository:
    @classmethod
    async def find_user_by_email(cls, email: EmailStr):
        """
        Find user by email
        """
        async with async_session_maker() as cursor:
            query = text(
                f"SELECT email FROM {Settings.DB_SCHEMA}.user WHERE email = :email"
            )
            result = await cursor.execute(query.params(email=email))
            row = result.fetchone()
            return row[0] if row else None

    @classmethod
    async def find_password_by_email(cls, email: EmailStr):
        """
        Get password by email
        """
        async with async_session_maker() as cursor:
            query = text(
                f"SELECT password FROM {Settings.DB_SCHEMA}.user WHERE email = :email"
            )
            result = await cursor.execute(query.params(email=email))
            row = result.fetchone()
            return row[0] if row else None

    @classmethod
    async def all_user_data(cls, email: EmailStr) -> UserJWTData | None:
        """
        Get all user data for payload
        """
        async with async_session_maker() as session:
            query = text(f"""
                SELECT user_id, email, "group", "role" 
                FROM public.user
                LEFT JOIN public.group USING (group_id)
                LEFT JOIN public.role USING (role_id)
                WHERE email = :email
            """)
            result = await session.execute(query.params(email=email))
            row = result.fetchone()
            print(row)
            if row:
                result = {
                    "user_id": row[0],  # Измените 'user_id' на 'id'
                    "email": row[1],
                    "group": row[2],
                    "role": row[3]
                }
                return result
            return None

    @classmethod
    async def create_user(cls, email: EmailStr, password: str):
        """
        Creating new user
        """
        user = await cls.find_user_by_email(email)
        if user:
            raise UserNotFoundException()

        async with async_session_maker() as cursor:
            query = text(
                f"INSERT INTO {Settings.DB_SCHEMA}.user (email, password) VALUES (:email, :password)"
            )
            await cursor.execute(query.params(email=email, password=password))
            await cursor.commit()
