import oracledb

oracledb.init_oracle_client(lib_dir='/Users/viktor/Downloads/instantclient_23_3')

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