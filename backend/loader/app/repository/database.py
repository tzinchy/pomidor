import psycopg2
from core.config import settings


def get_connection():
    return psycopg2.connect(
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME,
        host=settings.project_management_setting.DB_HOST,
    )

def get_source_connection(): 
    return psycopg2.connect(
        user=settings.dashboard_setting.DB_DASHBORD_USER,
        password=settings.dashboard_setting.DB_DASHBORD_PASSWORD,
        port=settings.dashboard_setting.DB_DASHBORD_PORT,
        database=settings.dashboard_setting.DB_DASHBORD_NAME,
        host=settings.dashboard_setting.DB_DASHBORD_HOST,      
    )