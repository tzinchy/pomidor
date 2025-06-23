from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from core.logger import logger

class CinReposiory:
    def __init__(self, session_maker : sessionmaker):
        self.db = session_maker

    async def get_cin(self):
        async with self.db() as session:
            query = text(
                "select * from cin "
                )
            logger.query(query)
            result = await session.execute(query)
            return result.fetchall()