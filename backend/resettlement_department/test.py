from app.core.config import settings
from datetime import datetime
import psycopg2

connection = psycopg2.connect(
    host=settings.project_management_setting.DB_HOST,
    user=settings.project_management_setting.DB_USER,
    password=settings.project_management_setting.DB_PASSWORD,
    port=settings.project_management_setting.DB_PORT,
    database=settings.project_management_setting.DB_NAME,
)

cursor = connection.cursor()
print(datetime.now())
cursor.execute('DELETE FROM public.offer')
connection.commit()
print(datetime.now())