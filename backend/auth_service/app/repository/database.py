from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import Settings

print(Settings.DATABASE_URL)

EGNINE = create_async_engine(Settings.DATABASE_URL)

auth_session = sessionmaker(EGNINE, class_=AsyncSession, expire_on_commit=False)

