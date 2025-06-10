from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from core.config import settings

import psycopg2

schema = settings.project_management_setting.DB_SCHEMA

project_managment_engine = create_async_engine(
    settings.project_management_setting.DATABASE_URL
)
project_managment_session = sessionmaker(project_managment_engine, class_=AsyncSession)

dashboard_engine = create_async_engine(settings.dashboard_setting.DATABASE_URL)
dashboard_session = sessionmaker(project_managment_engine, class_=AsyncSession)



def get_db_connection_dashboard():
    return psycopg2.connect(
        host=settings.dashboard_setting.DB_DASHBORD_HOST,
        user=settings.dashboard_setting.DB_DASHBORD_USER,
        password=settings.dashboard_setting.DB_DASHBORD_PASSWORD,
        port=settings.dashboard_setting.DB_DASHBORD_PORT,
        database=settings.dashboard_setting.DB_DASHBORD_NAME,
    )


def get_db_connection():
    return psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME,
    )
