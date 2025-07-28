from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from core.logger import logger


class EnvRepository:
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_env_history(self):
        async with self.db() as session:
            query = text(
                "SELECT id, name, (updated_at)::varchar, success FROM env.data_updates"
            )
            logger.query(query)
            result = await session.execute(query)
            return result.fetchall()
