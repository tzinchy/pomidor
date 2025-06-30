from sqlalchemy import text, select, insert, update
from sqlalchemy.orm import sessionmaker
from core.logger import logger
from models.cin import Cin


class CinRepository:  # Fixed typo in class name
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_cin(self):
        async with self.db() as session:
            query = text("SELECT * FROM test_cin")
            logger.query(query)
            result = await session.execute(query)

            # Properly convert SQLAlchemy result to dictionaries
            return [dict(row._mapping) for row in result]

    async def update_cin(self, cin):
        async with self.db() as session:
            # Convert Pydantic model to dict
            cin_data = cin.dict()
            
            # If cin_id is provided, we assume it's an update
            if cin.cin_id:
                stmt = (
                    update(Cin)
                    .where(Cin.cin_id == cin.cin_id)
                    .values(**cin_data)
                    .execution_options(synchronize_session="fetch")
                )
            else:
                # If no cin_id, it's an insert
                stmt = insert(Cin).values(**cin_data)
            
            await session.execute(stmt)
            await session.commit()

    async def create_cin(self, cin):
        async with self.db() as session:
            try:
                data = cin.dict(exclude_unset=True)
                stmt = insert(Cin).values(**data).returning(Cin)
                result = await session.execute(stmt)
                new_cin = result.scalar_one()
                await session.commit()
                return new_cin
                
            except Exception as e:
                await session.rollback()
                raise Exception("Ошибка при создании записи") from e
            
