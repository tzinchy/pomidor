from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import Settings, DashboardSetting

schema = Settings.DB_SCHEMA

up_engine = create_async_engine(Settings.DATABASE_URL)
dashboard_engine = create_async_engine(DashboardSetting.DATABASE_URL)

async_session_maker = sessionmaker(up_engine, class_=AsyncSession)
dashboard_session = sessionmaker(dashboard_engine, class_=AsyncSession)
