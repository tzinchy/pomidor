from sqlalchemy import text
from schema.apartment import ApartType
import logging
from utils.sql_reader import read_sql_query
from core.config import RECOMMENDATION_FILE_PATH

logger = logging.getLogger(__name__)


class ApartmentRepository:

    def __init__(self, session_maker):
        self.db = session_maker  # Это sessionmaker

    async def get_districts(self, apart_type: str) -> list[str]:
        """
        Получить уникальные районы.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        table = "old_apart" if apart_type == "OldApart" else "new_apart"
        query = f"""
            SELECT DISTINCT district 
            FROM {table}
            ORDER BY district
        """
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                result = await session.execute(text(query))
                return [row[0] for row in result if row[0] is not None]
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

    async def get_municipal_district(self, apart_type: str, districts: list[str]) -> list[str]:
        """
        Получить уникальные области по районам.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        table = "old_apart" if apart_type == "OldApart" else "new_apart"
        params = {}
        placeholders = []
        for i, district in enumerate(districts):
            key = f"district_{i}"
            placeholders.append(f":{key}")
            params[key] = district
        placeholders_str = ", ".join(placeholders)
        query = f"""
            SELECT DISTINCT municipal_district
            FROM {table}
            WHERE district IN ({placeholders_str})
            ORDER BY municipal_district
        """
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                logger.info(f"Params: {params}")
                result = await session.execute(text(query), params)
                return [row[0] for row in result if row[0] is not None]
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

    async def get_house_addresses(self, apart_type: str, municipal_districts: list[str]) -> list[str]:
        """
        Получить уникальные адреса домов по областям и районам (если указаны)
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        table = "old_apart" if apart_type == "OldApart" else "new_apart"
        params = {}
        placeholders = []
        for i, municipal in enumerate(municipal_districts):
            key = f"municipal_{i}"
            placeholders.append(f":{key}")
            params[key] = municipal
        placeholders_str = ", ".join(placeholders)
        query = f"""
            SELECT DISTINCT house_address
            FROM {table}
            WHERE municipal_district IN ({placeholders_str})
            ORDER BY house_address
        """
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                logger.info(f"Params: {params}")
                result = await session.execute(text(query), params)
                return [row[0] for row in result if row[0] is not None]
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

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
        area_type: str = 'full_living_area',
    ) -> list[dict]:
        """
        Получаем все квартиры с учетом опциональных фильтров.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")
        if area_type not in ['full_living_area', 'total_living_area', 'living_area']:
            raise ValueError(f"Invalid area type: {area_type}")

        conditions = ["rn = 1"]
        params = {}

        # Формируем условия для каждого переданного параметра
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
            conditions.append(f"municipal_district IN ({', '.join(municipal_placeholders)})")
        
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

        # Условия для площади
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

        # Формируем запрос в зависимости от типа квартир
        if apart_type == "OldApart":
            query = f"""
                WITH ranked_apartments AS (
                    SELECT
                        house_address,
                        apart_number,
                        district,
                        municipal_district,
                        floor,
                        fio,
                        full_living_area,
                        total_living_area,
                        living_area,
                        room_count,
                        type_of_settlement,
                        status.status,
                        o.notes,
                        affair_id,
                        ROW_NUMBER() OVER (PARTITION BY oa.affair_id ORDER BY o.sentence_date DESC, o.answer_date DESC) AS rn
                    FROM
                        old_apart oa
                    LEFT JOIN
                        offer o USING (affair_id)
                    LEFT JOIN
                        status ON o.status_id = status.status_id
                )
                SELECT *
                FROM ranked_apartments
                WHERE {where_clause}
                ORDER BY full_living_area
            """
        else:
            query = f"""
                WITH clr_dt AS (
                    SELECT 
                        affair_id, 
                        (KEY)::int AS new_apart_id, 
                        sentence_date, 
                        answer_date, 
                        (VALUE->'status_id')::int AS status_id 
                    FROM 
                        offer, 
                        jsonb_each(new_aparts)
                ),
                ranked_apartments AS (
                    SELECT 
                        na.house_address, 
                        na.apart_number, 
                        na.district, 
                        na.municipal_district,
                        na.floor,
                        na.full_living_area,
                        na.total_living_area, 
                        na.living_area, 
                        na.room_count, 
                        na.type_of_settlement, 
                        na.notes, 
                        na.new_apart_id,
                        s.status AS status,
                        ROW_NUMBER() OVER (
                            PARTITION BY na.new_apart_id 
                            ORDER BY o.sentence_date DESC, o.answer_date DESC 
                        ) AS rn
                    FROM 
                        new_apart na
                    LEFT JOIN 
                        clr_dt as o on o.new_apart_id = na.new_apart_id
                    LEFT JOIN 
                        status s ON o.status_id = s.status_id
                )
                SELECT *
                FROM ranked_apartments
                WHERE {where_clause}
                ORDER BY status;
            """
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                logger.info(f"Params: {params}")
                result = await session.execute(text(query), params)
                return [dict(row._mapping) for row in result]
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

    async def get_apartment_by_id(self, apartment_id: int, apart_type: str) -> dict:
        """
        Получить всю информацию о квартире по ID.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        query_params = {"apartment_id": apartment_id}
        
        if apart_type == "NewApartment":
            query = """
                WITH unnset_offer AS (
                    SELECT 
                        affair_id,
                        (KEY)::integer as new_apart_id,
                        (VALUE->'status_id')::integer AS status_id,
                        sentence_date, 
                        answer_date
                    FROM offer, 
                    jsonb_each(new_aparts)
                ),
                joined_aparts AS (
                    SELECT 
                        o.new_apart_id,
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'house_address', old_apart.house_address,
                                'apart_number', old_apart.apart_number,
                                'district', old_apart.district,
                                'municipal_district', old_apart.municipal_district,
                                'full_living_area', old_apart.full_living_area,
                                'total_living_area', old_apart.total_living_area,
                                'living_area', old_apart.living_area,
                                'room_count', old_apart.room_count,
                                'type_of_settlement', old_apart.type_of_settlement,
                                'notes', old_apart.notes,
                                'status', s.status,
                                'sentence_date', o.sentence_date :: DATE,
                                'answer_date', o.answer_date :: DATE
                            ) ORDER BY sentence_date DESC, answer_date DESC
                        ) AS old_apartments
                    FROM 
                        unnset_offer o
                    LEFT JOIN 
                        old_apart ON old_apart.affair_id = o.affair_id
                    LEFT JOIN 
                        status s ON o.status_id = s.status_id
                    GROUP BY 
                        o.new_apart_id
                )
                SELECT 
                    new_apart.new_apart_id, 
                    new_apart.house_address,
                    new_apart.apart_number,
                    new_apart.district,
                    new_apart.municipal_district,
                    new_apart.full_living_area,
                    new_apart.total_living_area,
                    new_apart.living_area,
                    new_apart.room_count,
                    new_apart.type_of_settlement,
                    joined_aparts.old_apartments
                FROM new_apart  
                LEFT JOIN joined_aparts USING (new_apart_id) 
                WHERE new_apart_id = :apartment_id
            """
        elif apart_type == "OldApart":
            query = """
                WITH unnset_offer AS (
                    SELECT 
                        affair_id,
                        (KEY)::integer as new_apart_id,
                        (VALUE->'status_id')::integer AS status_id,
                        sentence_date, 
                        answer_date
                    FROM offer, 
                    jsonb_each(new_aparts)
                ),
                joined_aparts AS (
                    SELECT 
                        affair_id,
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'house_address', na.house_address,
                                'apart_number', na.apart_number,
                                'district', na.district,
                                'municipal_district', na.municipal_district,
                                'full_living_area', na.full_living_area,
                                'total_living_area', na.total_living_area,
                                'living_area', na.living_area,
                                'room_count', na.room_count,
                                'type_of_settlement', na.type_of_settlement,
                                'notes', na.notes,
                                'status', s.status,
                                'sentence_date', o.sentence_date :: DATE,
                                'answer_date', o.answer_date :: DATE
                            ) ORDER BY sentence_date DESC, answer_date DESC
                        ) AS new_apartments
                    FROM 
                        unnset_offer o
                    LEFT JOIN 
                        new_apart na ON o.new_apart_id = na.new_apart_id
                    LEFT JOIN 
                        status s ON o.status_id = s.status_id
                    GROUP BY 
                        o.affair_id
                )
                SELECT 
                    old_apart.affair_id, 
                    old_apart.house_address,
                    old_apart.apart_number,
                    old_apart.district,
                    old_apart.municipal_district,
                    old_apart.full_living_area,
                    old_apart.total_living_area,
                    old_apart.living_area,
                    old_apart.room_count,
                    old_apart.type_of_settlement,
                    joined_aparts.new_apartments
                FROM old_apart  
                LEFT JOIN joined_aparts USING (affair_id) 
                WHERE affair_id = :apartment_id         
            """
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")

        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                result = await session.execute(text(query), query_params)
                data = result.fetchone()
                if not data:
                    raise ValueError(f"Apartment with ID {apartment_id} not found")
                return dict(data._mapping)
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

    async def get_house_address_with_room_count(self, apart_type):
        if apart_type == "NewApartment":
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/AvaliableNewApartAddress.sql')
        elif apart_type == "OldApart":
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/AvaliableOldApartAddress.sql')
        else:
            raise ValueError("Invalid apartment type")

        async with self.db() as session:
            try:
                result = await session.execute(text(query))
                return result.fetchall()
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

    async def switch_apartment(self, first_apartment_id, second_apartment_id):
        query = "SELECT swap_new_aparts(:first_apartment_id, :second_apartment_id)"
        params = {
            "first_apartment_id": int(first_apartment_id),
            "second_apartment_id": int(second_apartment_id)
        }
        async with self.db() as session:
            try:
                result = await session.execute(text(query), params)
                await session.commit()

                # Преобразуем результат в сериализуемый формат
                rows = result.fetchall()
                if rows:
                    # Если результат содержит строки, преобразуем их в список словарей
                    serialized_result = [row._asdict() for row in rows]  # Используем ._asdict()
                    return serialized_result
                else:
                    # Если результат пуст, возвращаем сообщение
                    return {"message": "No rows affected"}

            except Exception as e:
                logger.error(f"Error switching apartments: {e}")
                raise