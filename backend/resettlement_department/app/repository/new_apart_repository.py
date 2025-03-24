from sqlalchemy import text
from core.config import RECOMMENDATION_FILE_PATH
from sqlalchemy.orm import sessionmaker
from utils.sql_reader import read_sql_query
from schema.apartment import ApartTypeSchema
from handlers.httpexceptions import SomethingWrong
import logging


logger = logging.getLogger(__name__)


class NewApartRepository:
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_districts(self) -> list[str]:
        async with self.db() as session:
            try:
                query = """SELECT DISTINCT district 
                        FROM new_apart
                        ORDER BY district"""
                result = await session.execute(text(query))
                return [row[0] for row in result if row[0] is not None]
            except Exception as error:
                print(error)
                raise

    async def get_municipal_district(self, districts: list[str]) -> list[str]:
        params = {}
        placeholders = []
        for i, district in enumerate(districts):
            key = f"district_{i}"
            placeholders.append(f":{key}")
            params[key] = district
        placeholders_str = ", ".join(placeholders)
        query = f"""
            SELECT DISTINCT municipal_district
            FROM new_apart
            WHERE district IN ({placeholders_str})
            ORDER BY municipal_district
        """
        async with self.db() as session:
            try:
                print(f"Executing query: {query}")
                print(f"Params: {params}")
                result = await session.execute(text(query), params)
                return [row[0] for row in result if row[0] is not None]
            except Exception as error:
                print(f"Error executing query: {error}")
                raise AttributeError

    async def get_house_addresses(self, municipal_districts: list[str]) -> list[str]:
        params = {}
        placeholders = []
        for i, municipal in enumerate(municipal_districts):
            key = f"municipal_{i}"
            placeholders.append(f":{key}")
            params[key] = municipal
        placeholders_str = ", ".join(placeholders)
        query = f"""
            SELECT DISTINCT house_address
            FROM new_apart
            WHERE municipal_district IN ({placeholders_str})
            ORDER BY house_address
        """
        async with self.db() as session:
            try:
                print(f"Executing query: {query}")
                print(f"Params: {params}")
                result = await session.execute(text(query), params)
                return [row[0] for row in result if row[0] is not None]
            except Exception as error:
                print(f"Error executing query: {error}")
                raise

    async def get_district_chain(self):
        async with self.db() as session:
            result = await session.execute(
                text("""
                SELECT 
                    jsonb_object_agg(district, municipal_districts) AS result
                FROM (
                    SELECT 
                        district, 
                        jsonb_agg(municipal_district) AS municipal_districts
                    FROM new_apart
                    GROUP BY district
                ) AS subquery;
            """)
            )

            rows = result.fetchall()
            if rows:
                return rows[0]._mapping["result"]
            return {}

    async def set_notes(self, apart_id: int, notes: str):
        async with self.db() as session:
            try:
                await session.execute(
                    text("""
                    UPDATE new_apart SET notes = :notes 
                    WHERE new_apart_id = :apart_id
                    """),
                    {"notes": notes, "apart_id": apart_id},
                )
                await session.commit()
                return {"status": "done"}
            except Exception as e:
                print(e)
                raise AttributeError

    async def get_apartments(
        self,
        apart_type: str,
        house_addresses: list[str] = None,
        districts: list[str] = None,
        municipal_districts: list[str] = None,
        floor: int = None,
        room_count: list[int] = None,
        min_area: float = None,
        max_area: float = None,
        area_type: str = "full_living_area",
        is_queue: bool = None,
        is_private: bool = None,
    ) -> list[dict]:
        if area_type not in ["full_living_area", "total_living_area", "living_area"]:
            raise ValueError(f"Invalid area type: {area_type}")

        conditions = ["rn = 1"]
        params = {}

        if house_addresses:
            addr_placeholders = []
            for i, addr in enumerate(house_addresses):
                key = f"house_addr_{i}"
                addr_placeholders.append(f":{key}")
                params[key] = addr
            conditions.append(f"house_address IN ({', '.join(addr_placeholders)})")

        if districts:
            district_placeholders = []
            for i, district in enumerate(districts):
                key = f"district_{i}"
                district_placeholders.append(f":{key}")
                params[key] = district
            conditions.append(f"district IN ({', '.join(district_placeholders)})")

        if municipal_districts:
            municipal_placeholders = []
            for i, municipal in enumerate(municipal_districts):
                key = f"municipal_{i}"
                municipal_placeholders.append(f":{key}")
                params[key] = municipal
            conditions.append(
                f"municipal_district IN ({', '.join(municipal_placeholders)})"
            )

        if floor is not None:
            conditions.append("floor = :floor")
            params["floor"] = floor

        if room_count:
            room_placeholders = []
            for i, room in enumerate(room_count):
                key = f"room_{i}"
                room_placeholders.append(f":{key}")
                params[key] = room
            conditions.append(f"room_count IN ({', '.join(room_placeholders)})")

        if is_queue is not None and apart_type == ApartTypeSchema.OLD:
            conditions.append("is_queue != 0")

        if is_private is not None and apart_type == ApartTypeSchema.NEW:
            conditions.append("is_private != 0")

        area_conditions = []
        if min_area is not None:
            area_conditions.append(f"{area_type} >= :min_area")
            params["min_area"] = min_area
        if max_area is not None:
            area_conditions.append(f"{area_type} <= :max_area")
            params["max_area"] = max_area
        if area_conditions:
            conditions.append(" AND ".join(area_conditions))

        where_clause = " AND ".join(conditions)

        query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/NewApartTable.sql")

        query = f"{query} WHERE {where_clause}"
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                logger.info(f"Params: {params}")
                result = await session.execute(text(query), params)

                return [row._mapping for row in result]
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                print(error)
                raise SomethingWrong
            
    async def get_apartment_by_id(self, apart_id: int) -> dict:
        query_params = {"apart_id": apart_id}

        query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/NewApartById.sql")

        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                result = await session.execute(text(query), query_params)
                data = result.fetchall()
                if not data:
                    raise ValueError(f"Apartment with ID {apart_id} not found")

                return [row._mapping for row in data][0]
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                print(error)
                raise SomethingWrong


    async def get_house_address_with_room_count(self):
        query = read_sql_query(
            f"{RECOMMENDATION_FILE_PATH}/AvaliableNewApartAddress.sql"
        )
        async with self.db() as session:
            try:
                result = await session.execute(text(query))
                return result.fetchall()
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise SomethingWrong

    
    async def set_private_for_new_aparts(self, new_apart_ids, status: bool = True):
        async with self.db() as session:
            try:

                placeholders = ", ".join(
                    [":id_" + str(i) for i in range(len(new_apart_ids))]
                )

                params = {"status": status}
                params.update({f"id_{i}": id for i, id in enumerate(new_apart_ids)})

                query = text(
                    f"UPDATE new_apart SET is_private = :status WHERE new_apart_id IN ({placeholders})"
                )

                # Передаем параметры в правильном формате
                await session.execute(query, params)
                await session.commit()
            except Exception as error:
                print(error)
                raise SomethingWrong(
                    "Something went wrong while updating the apartments."
                )
            
    async def cancell_matching_apart(self, apart_id):
        async with self.db() as session:
            try:
                result = await session.execute(
                    text("""
                    WITH new_apart_in_offer AS (
                            SELECT offer_id
                                FROM offer,
                                jsonb_each(new_aparts)
                                where (key)::int = :apart_id)
                        DELETE FROM offer
                        WHERE offer_id = (SELECT MAX(offer_id) FROM new_apart_in_offer);"""),
                    {"apart_id": apart_id},
                )
                await session.commit()
                return result
            except Exception as error:
                print(error)
                raise SomethingWrong