from sqlalchemy import text, select, insert, update
from sqlalchemy.orm import sessionmaker
from core.logger import logger
from models.cin import Cin


class CinRepository:  # Fixed typo in class name
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_cin(self, user_districts : list[str] = None):
        try:
            async with self.db() as session:
                # Base query
                query = "SELECT * FROM test_cin"
                params = {}
                
                # Add WHERE clause if districts are provided
                if user_districts:
                    params = {f"district_{i}": district 
                            for i, district in enumerate(user_districts)}
                    placeholders = ", ".join(f":{key}" for key in params.keys())
                    query += f" WHERE district IN ({placeholders})"
                
                # Always add ORDER BY
                query += " ORDER BY cin_id"
        
            logger.query(query)
            result = await session.execute(text(query), params)

            # Properly convert SQLAlchemy result to dictionaries
            return [dict(row._mapping) for row in result]
        except Exception as e: 
            print(e)

    async def update_cin(self, cin):
        async with self.db() as session:
            cin_data = cin.dict()
            
            if cin.cin_id:
                stmt = (
                    update(Cin)
                    .where(Cin.cin_id == cin.cin_id)
                    .values(**cin_data)
                    .execution_options(synchronize_session="fetch")
                )
            else:
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
            
