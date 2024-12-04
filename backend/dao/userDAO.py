from database import async_session_maker
from pydantic import EmailStr
from sqlalchemy import text
from config import Settings
from auth.httpexceptions import UserNotFoundException
from schema.user import UserLoginShema, UserSchemaForDump
import jwt

class UserDAO:
    """
    Базовый класс для работы с пользовательскими данными.
    Включает методы для получения данных пользователя, пароля и информации для создания JWT.
    """
    @classmethod
    async def find_user_by_email(cls, email: EmailStr):
        """
        Получение пользователя по email.
        Возвращает пользователя, если он найден, иначе None.
        """
        async with async_session_maker() as cursor:
            query = text(f'SELECT email FROM {Settings.DB_SCHEMA}.user WHERE email = :email')
            result = await cursor.execute(query.params(email=email))
            result = result.fetchone()[0] 
            return result

    @classmethod
    async def find_password_by_email(cls, email: EmailStr):
        """
        Получение пароля пользователя по email.
        Возвращает пароль, если найден, иначе None.
        """
        async with async_session_maker() as cursor:
            query = text(f'SELECT password FROM {Settings.DB_SCHEMA}.user WHERE email = :email')
            result = await cursor.execute(query.params(email=email))
            result = result.fetchone()[0]
            return result

    @classmethod
    async def find_user_info_for_jwt(cls, email: EmailStr):
        """
        Получение всей информации о пользователе для создания JWT (включая group и role).
        """
        async with async_session_maker() as session:
            query = text(f'''
                SELECT user_id, email, "group", "role" 
                FROM public.user
                LEFT JOIN public.group using (group_id)
                LEFT JOIN public.role using (role_id)
                WHERE email = :email
            ''')
            result = await session.execute(query.params(email=email))
            row = result.fetchone()

            if row:
                # Преобразуем кортеж в словарь
                return {
                    "id": row[0],
                    "email": row[1],
                    "group": row[2],
                    "role": row[3],
                }
            return None
    
    @classmethod
    async def create_user(cls, email: EmailStr, password: str):
        # Перед созданием проверим, существует ли пользователь с таким email
        user = await cls.find_user_by_email(email)
        print(user)
        if user:
            raise UserNotFoundException()  # Выбрасываем ошибку, если пользователь найден

        async with async_session_maker() as cursor:
            query = text(f'INSERT INTO {Settings.DB_SCHEMA}.user (email, password) VALUES (:email, :password)')
            await cursor.execute(query.params(email=email, password=password))
            await cursor.commit()

    def create_jwt(user_payload: UserSchemaForDump) -> str:
        return jwt.encode(user_payload.model_dump(), Settings.SECRET_KEY, algorithm="HS256")
