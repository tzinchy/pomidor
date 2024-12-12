# app/repository/user_repository.py
from repository.database import async_session_maker
from pydantic import EmailStr
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError
from core.config import Settings

class UserRepository:
    @classmethod
    async def find_user_by_email(cls, email: EmailStr) -> dict | None:
        """Find user by email."""
        async with async_session_maker() as session:
            query = text(f"""
                SELECT user_id, email 
                FROM {Settings.DB_SCHEMA}.user 
                WHERE email = :email
            """)
            result = await session.execute(query.params(email=email))
            row = result.fetchone()
            return {"user_id": row[0], "email": row[1]} if row else None

    @classmethod
    async def find_password_by_email(cls, email: EmailStr) -> str | None:
        """Get password hash by email."""
        async with async_session_maker() as session:
            query = text(f"""
                SELECT password 
                FROM {Settings.DB_SCHEMA}.user 
                WHERE email = :email
            """)
            result = await session.execute(query.params(email=email))
            row = result.fetchone()
            return row[0] if row else None

    @classmethod
    async def does_user_exist(cls, email: EmailStr) -> bool:
        """Check if a user exists by email."""
        async with async_session_maker() as session:
            query = text(f"SELECT 1 FROM {Settings.DB_SCHEMA}.user WHERE email = :email")
            result = await session.execute(query.params(email=email))
            return result.scalar() is not None

    @classmethod
    async def create_user(cls, email: EmailStr, password: str) -> None:
        """Create a new user."""
        async with async_session_maker() as session:
            query = text(f"""
                INSERT INTO {Settings.DB_SCHEMA}.user (email, password) 
                VALUES (:email, :password)
            """)
            await session.execute(query.params(email=email, password=password))
            await session.commit()

    @staticmethod
    async def update_password(email: str, new_password: str) -> None:
        """Update a user's password."""
        async with async_session_maker() as session:
            query = text(f"""
                UPDATE {Settings.DB_SCHEMA}.user 
                SET password = :new_password 
                WHERE email = :email
            """)
            await session.execute(query.params(email=email, new_password=new_password))
            await session.commit()


    @classmethod
    async def find_user_data_for_jwt(cls, email: EmailStr) -> dict | None:
        """Get user data needed for JWT payload."""
        async with async_session_maker() as session:
            query = text(f"""
                SELECT user_id, email, "group", "role" 
                FROM {Settings.DB_SCHEMA}.user
                LEFT JOIN {Settings.DB_SCHEMA}.group USING (group_id)
                LEFT JOIN {Settings.DB_SCHEMA}.role USING (role_id)
                WHERE email = :email
            """)
            result = await session.execute(query.params(email=email))
            row = result.fetchone()
            return {
                "user_id": row[0],
                "email": row[1],
                "group": row[2],
                "role": row[3]
            } if row else None
