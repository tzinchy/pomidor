from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import Settings, DashboardSetting

import psycopg2

schema = Settings.DB_SCHEMA

up_engine = create_async_engine(Settings.DATABASE_URL)
dashboard_engine = create_async_engine(DashboardSetting.DATABASE_URL)

async_session_maker = sessionmaker(up_engine, class_=AsyncSession)
dashboard_session = sessionmaker(dashboard_engine, class_=AsyncSession)

def get_db_connection_dashboard():
    return psycopg2.connect(
        host = DashboardSetting.DB_DASHBORD_HOST,
        user = DashboardSetting.DB_DASHBORD_USER,
        password = DashboardSetting.DB_DASHBORD_PASS,
        port = DashboardSetting.DB_DASHBORD_PORT,
        database = DashboardSetting.DB_DASHBORD_NAME
    )

def get_db_connection():
    return psycopg2.connect(
        host=Settings.DB_HOST,
        port=Settings.DB_PORT,
        database=Settings.DB_NAME,
        user=Settings.DB_USER,
        password=Settings.DB_PASS,
    )