import oracledb
import os
import platform
from pathlib import Path

current_os = platform.system()
print(current_os)
folder_name = ''
if current_os == 'Linux':
    folder_name = 'linux_instantclient_23'
elif current_os == 'Darwin':
    folder_name = 'macos_instantclient_23'
elif current_os == 'Windows':
    folder_name = 'win64_instantclient_23'

INSTANT_CLIENT_DIR = Path(__file__).resolve().parent.parent.parent / f"oracle/{folder_name}"
oracledb.init_oracle_client(lib_dir=str(INSTANT_CLIENT_DIR))

class OracleClient:
    def __init__(self, user: str, password: str, host: str, port: int, service_name: str):
        self.dsn = f"{host}:{port}/{service_name}"
        self.user = user
        self.password = password
        self.pool = None

    def init_pool(self, min=1, max=5, increment=1):
        self.pool = oracledb.create_pool(
            user=self.user,
            password=self.password,
            dsn=self.dsn,
            min=min,
            max=max,
            increment=increment,
        )

    def fetchall(self, query: str, params: tuple = ()) -> list[dict]:
        with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                columns = [col[0] for col in cursor.description]
                return [dict(zip(columns, row)) for row in cursor.fetchall()]

    def fetchone(self, query: str, params: tuple = ()) -> dict | None:
        with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                row = cursor.fetchone()
                if row:
                    columns = [col[0] for col in cursor.description]
                    return dict(zip(columns, row))
                return None

    def execute(self, query: str, params: tuple = ()) -> None:
        with self.pool.acquire() as conn:
            with conn.cursor() as cursor:
                cursor.execute(query, params)
                conn.commit()