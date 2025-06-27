from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from core.logger import logger


class CinRepository:  # Fixed typo in class name
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_cin(self):
        async with self.db() as session:
            query = text("SELECT * FROM cin")
            logger.query(query)
            result = await session.execute(query)

            # Properly convert SQLAlchemy result to dictionaries
            return [dict(row._mapping) for row in result]
