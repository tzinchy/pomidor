from repository.database import async_session_maker
from pydantic import EmailStr
from sqlalchemy import text
from core.config import Settings
from core.httpexceptions import UserNotFoundException


class UserRepository:
    # Пример исправленного метода для получения пользователя по email
    @classmethod
    async def find_user_by_email(cls, email: EmailStr):
        """
        Получение пользователя по email.
        Возвращает пользователя, если он найден, иначе None.
        """
        async with async_session_maker() as cursor:
            query = text(
                f"SELECT email FROM {Settings.DB_SCHEMA}.user WHERE email = :email"
            )
            result = await cursor.execute(query.params(email=email))
            row = result.fetchone()  # Получаем первую строку результата
            if row:
                return row[0]  # Если строка найдена, возвращаем email
            return None  # Если нет, возвращаем None

    # Аналогично для поиска пароля
    @classmethod
    async def find_password_by_email(cls, email: EmailStr):
        """
        Получение пароля пользователя по email.
        Возвращает пароль, если найден, иначе None.
        """
        async with async_session_maker() as cursor:
            query = text(
                f"SELECT password FROM {Settings.DB_SCHEMA}.user WHERE email = :email"
            )
            result = await cursor.execute(query.params(email=email))
            row = result.fetchone()  # Получаем первую строку результата
            if row:
                return row[0]  # Если строка найдена, возвращаем пароль
            return None  # Если нет, возвращаем None


    @classmethod
    async def find_user_info_for_jwt(cls, email: EmailStr):
        """
        Получение всей информации о пользователе для создания JWT
        """
        async with async_session_maker() as session:
            query = text(f"""
                SELECT user_id, email, "group", "role" 
                FROM public.user
                LEFT JOIN public.group using (group_id)
                LEFT JOIN public.role using (role_id)
                WHERE email = :email
            """)
            result = await session.execute(query.params(email=email))
            row = result.fetchone()

            if row:
                return {
                    "id": row[0],
                    "email": row[1],
                    "group": row[2],
                    "role": row[3],
                }
            return None

    @classmethod
    async def create_user(cls, email: EmailStr, password: str):
        user = await cls.find_user_by_email(email)
        print(user)
        if user:
            raise UserNotFoundException()

        async with async_session_maker() as cursor:
            query = text(
                f"INSERT INTO {Settings.DB_SCHEMA}.user (email, password) VALUES (:email, :password)"
            )
            await cursor.execute(query.params(email=email, password=password))
            await cursor.commit()
