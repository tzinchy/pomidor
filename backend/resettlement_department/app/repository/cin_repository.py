from sqlalchemy import text, select, insert, update
from sqlalchemy.orm import sessionmaker
from core.logger import logger
from models.cin import Cin
from typing import Optional
from schema.cin import CreateCin


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

    async def update_cin(self, cin : Cin):
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

    async def create_cin(self, cin : CreateCin):
        async with self.db() as session:
            try:
                data = cin.model_dump()
                stmt = insert(Cin).values(**data).returning(Cin)
                result = await session.execute(stmt)
                new_cin = result.scalar_one()
                await session.commit()
                return new_cin
                
            except Exception as e:
                await session.rollback()
                raise Exception("Ошибка при создании записи") from e
            
    async def get_cin_districts(self, user_districts: Optional[list[str]] = None) -> list[str]:
        print(user_districts)
        try:
            async with self.db() as session:
                # Base query
                query = "SELECT DISTINCT district FROM old_apart"
                params = {}
                
                # Add WHERE clause if districts are provided
                if user_districts:
                    params = {f"district_{i}": district 
                            for i, district in enumerate(user_districts)}
                    placeholders = ", ".join(f":{key}" for key in params.keys())
                    query += f" WHERE district IN ({placeholders})"
                
                # Always add ORDER BY
                query += " ORDER BY district"
                print(query.format(params))
                # Execute query
                result = await session.execute(text(query), params or None)
                districts = [row[0] for row in result if row[0] is not None]
                print(districts)
                return districts

        except Exception as e:
            print(f"Database error in get_districts: {str(e)}", exc_info=True)
            raise e

    async def get_cin_municipal_district(self,districts: list[str] = None) -> list[str]:
        params = {}
        placeholders = []
        query = """
            SELECT DISTINCT municipal_district
            FROM old_apart
        """

        if districts:  # Исправлено: districts вместо district
            for i, district in enumerate(districts):
                key = f"district_{i}"
                placeholders.append(f":{key}")
                params[key] = district

            placeholders_str = ", ".join(placeholders)
            query += f"""
                WHERE district IN ({placeholders_str})
                ORDER BY municipal_district
            """

        async with self.db() as session:
            result = await session.execute(text(query), params)
            return [row[0] for row in result if row[0] is not None] or []

    async def get_cin_house_addresses(
        self, municipal_districts: list[str] = None, district : list[str] = None,
    ) -> list[str]:
        params = {}
        query = "SELECT DISTINCT house_address FROM new_apart WHERE 1=1"
        if district: 
            # Создаем список параметров для IN-условия
            placeholders = [f":district_{i}" for i in range(len(municipal_districts))]
            params = {
                f"district_{i}": dist for i, dist in enumerate(municipal_districts)
            }

            # Добавляем условие с пробелом перед WHERE
            query += f" AND district IN ({', '.join(placeholders)})"

        if municipal_districts:
            # Создаем список параметров для IN-условия
            placeholders = [f":municipal_{i}" for i in range(len(municipal_districts))]
            params = {
                f"municipal_{i}": dist for i, dist in enumerate(municipal_districts)
            }

            # Добавляем условие с пробелом перед WHERE
            query += f" AND municipal_district IN ({', '.join(placeholders)})"

        # Всегда добавляем сортировку
        query += " ORDER BY house_address"

        print("Final query:", query)
        print("Params:", params)

        async with self.db() as session:
            try:
                result = await session.execute(text(query), params)
                addresses = [row[0] for row in result if row[0] is not None]
                return addresses if addresses else []
            except Exception as e:
                raise e