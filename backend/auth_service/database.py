from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from passlib.context import CryptContext
from sqlalchemy import text

from config import Settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

schema = Settings.DB_SCHEMA

engine = create_async_engine(Settings.DATABASE_URL)

async_session_maker = sessionmaker(engine, class_=AsyncSession)
