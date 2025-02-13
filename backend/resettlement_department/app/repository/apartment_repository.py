from sqlalchemy import text
from schema.apartment import ApartType
import logging
from utils.sql_reader import read_sql_query
from core.config import RECOMMENDATION_FILE_PATH

logger = logging.getLogger(__name__)


class ApartmentRepository:

    def __init__(self, session_maker):
        self.db = session_maker  # Это sessionmaker

    async def _execute_query(self, query: str, params: dict) -> list[tuple]:
        """
        Выполнение запроса и возврат результата.
        """
        async with self.db() as session:  # Создаем сессию
            try:
                logger.info(f"Executing query: {query}")
                logger.info(f"Params: {params}")
                result = await session.execute(text(query), params)  # Используем session.execute
                return result.fetchall()
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise

    def _build_placeholders(self, values: list, prefix: str) -> tuple[str, dict]:
        """
        Создать placeholders и параметры для подстановки.
        Поддерживает строки и числа.
        """
        placeholders = ", ".join(f":{prefix}_{i}" for i in range(len(values)))
        params = {
            f"{prefix}_{i}": str(value).strip() if isinstance(value, str) else value
            for i, value in enumerate(values)
        }
        return placeholders, params

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
        result = await self._execute_query(query, {})
        return [row[0] for row in result if row[0] is not None]

    async def get_municipal_district(self, apart_type: str, districts: list[str]) -> list[str]:
        """
        Получить уникальные области по районам.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        table = "old_apart" if apart_type == "OldApart" else "new_apart"
        placeholders, params = self._build_placeholders(districts, "district")
        query = f"""
            SELECT DISTINCT municipal_district
            FROM {table}
            WHERE district IN ({placeholders})
            ORDER BY municipal_district
        """
        result = await self._execute_query(query, params)
        return [row[0] for row in result if row[0] is not None]

    async def get_house_addresses(self, apart_type: str, municipal_districts: list[str]) -> list[str]:
        """
        Получить уникальные адреса домов по областям и районам (если указаны)
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        table = "old_apart" if apart_type == "OldApart" else "new_apart"
        placeholders, params = self._build_placeholders(municipal_districts, "municipal_districts")
        query = f"""
            SELECT DISTINCT house_address
            FROM {table}
            WHERE municipal_district IN ({placeholders})
            ORDER BY house_address
        """
        result = await self._execute_query(query, params)
        return [row[0] for row in result if row[0] is not None]

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

        conditions = []
        params = {}

        # Формируем условия для каждого переданного параметра
        if house_addresses:
            placeholders, addr_params = self._build_placeholders(house_addresses, "house_address")
            conditions.append(f"house_address IN ({placeholders})")
            params.update(addr_params)
        
        if districts:
            placeholders, district_params = self._build_placeholders(districts, "district")
            conditions.append(f"district IN ({placeholders})")
            params.update(district_params)
        
        if municipal_districts:
            placeholders, municipal_params = self._build_placeholders(municipal_districts, "municipal")
            conditions.append(f"municipal_district IN ({placeholders})")
            params.update(municipal_params)
        
        if floor is not None:
            conditions.append("floor = :floor")
            params["floor"] = floor

        if room_count:
            placeholders, room_params = self._build_placeholders(room_count, "room")
            conditions.append(f"room_count IN ({placeholders})")
            params.update(room_params)

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

        # Всегда фильтруем по последнему предложению
        conditions.append("rn = 1")

        # Собираем полное условие WHERE
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
                WHERE 1=1 and {where_clause}
                ORDER BY full_living_area
            """
        else:
            query = f"""

				WITH clr_dt AS (SELECT 
                        affair_id, 
                        (KEY)::int AS new_apart_id, 
                        sentence_date, 
                        answer_date, 
                        (VALUE->'status_id')::int AS status_id 
                    FROM 
                        offer, 
                        jsonb_each(new_aparts)),
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
            WHERE 1=1 and {where_clause}
            ORDER BY status;
            """
        print(query, params)
        result = await self._execute_query(query, params)
        print(len(result))
        return [dict(row._mapping) for row in result]

    async def get_apartment_by_id(self, apartment_id: int, apart_type: str) -> dict:
        """
        Получить всю информацию о квартире по ID.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        if apart_type == "NewApartment":
            query = f'''WITH unnset_offer AS (
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
                lft AS (
                    SELECT 
                        o.affair_id,
                        o.new_apart_id,
                        na.house_address,
                        na.apart_number,
                        na.district,
                        na.municipal_district,
                        na.full_living_area,
                        na.total_living_area,
                        na.living_area,
                        na.room_count,
                        na.type_of_settlement,
                        na.notes,
                        s.status,
                        o.sentence_date,
                        o.answer_date
                    FROM 
                        unnset_offer o 
                        LEFT JOIN new_apart na USING (new_apart_id)
                        LEFT JOIN status s ON o.status_id = s.status_id
                ),
                old_apart_data AS (
                    SELECT 
                        oa.affair_id,
                        oa.house_address,
                        oa.apart_number,
                        oa.district,
                        oa.municipal_district,
                        oa.full_living_area,
                        oa.total_living_area,
                        oa.living_area,
                        oa.room_count,
                        oa.type_of_settlement,
                        o.sentence_date,
                        o.answer_date
                    FROM 
                        old_apart oa
                        LEFT JOIN unnset_offer o ON oa.affair_id = o.affair_id
                )
                SELECT 
                                    na.new_apart_id,
                                            na.house_address,
                                            na.apart_number,
                                            na.district,
                                            na.municipal_district,
                                            na.full_living_area,
                                            na.total_living_area,
                                            na.living_area,
                                            na.room_count,
                        jsonb_agg(
                            jsonb_build_object(
                                'house_address', oa.house_address,
                                'apart_number', oa.apart_number,
                                'district', oa.district,
                                'municipal_district', oa.municipal_district,
                                'full_living_area', oa.full_living_area,
                                'total_living_area', oa.total_living_area,
                                'living_area', oa.living_area,
                                'room_count', oa.room_count,
                                'type_of_settlement', oa.type_of_settlement,
                                'sentence_date', oa.sentence_date,
                                'answer_date', oa.answer_date
                            ) ORDER BY 
                                oa.sentence_date DESC NULLS LAST, 
                                oa.answer_date DESC NULLS LAST
                        )
                    AS old_apartments
                FROM 
                    lft na
                    LEFT JOIN old_apart_data oa ON na.affair_id = oa.affair_id
                    where new_apart_id = {apartment_id} 
                GROUP BY 
                                        na.new_apart_id,
                                            na.house_address,
                                            na.apart_number,
                                            na.district,
                                            na.municipal_district,
                                            na.full_living_area,
                                            na.total_living_area,
                                            na.living_area,
                                            na.room_count
                ORDER BY 
                    na.new_apart_id;'''
        elif apart_type == "OldApart":
            query = f'''WITH unnset_offer AS (
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
            lft AS (
                SELECT 
                    o.affair_id,
                    na.house_address,
                    na.apart_number,
                    na.district,
                    na.municipal_district,
                    na.full_living_area,
                    na.total_living_area,
                    na.living_area,
                    na.room_count,
                    na.type_of_settlement,
                    na.notes,
                    s.status,
                    o.sentence_date,
                    o.answer_date
                FROM 
                    unnset_offer o 
                    LEFT JOIN new_apart na USING (new_apart_id)
                    LEFT JOIN status s ON o.status_id = s.status_id
            ),
            old_apart_data AS (
                SELECT 
                    oa.affair_id,
                    oa.house_address,
                    oa.apart_number,
                    oa.district,
                    oa.municipal_district,
                    oa.full_living_area,
                    oa.total_living_area,
                    oa.living_area,
                    oa.room_count,
                    oa.type_of_settlement
                FROM 
                    old_apart oa
            )
            SELECT 
                oa.affair_id,
                oa.house_address,
                oa.apart_number,
                oa.district,
                oa.municipal_district,
                oa.full_living_area,
                oa.total_living_area,
                oa.living_area,
                oa.room_count,
                oa.type_of_settlement,
                jsonb_agg(
                    jsonb_build_object(
                        'house_address', lft.house_address,
                        'apart_number', lft.apart_number,
                        'district', lft.district,
                        'municipal_district', lft.municipal_district,
                        'full_living_area', lft.full_living_area,
                        'total_living_area', lft.total_living_area,
                        'living_area', lft.living_area,
                        'room_count', lft.room_count,
                        'type_of_settlement', lft.type_of_settlement,
                        'notes', lft.notes,
                        'status', lft.status,
                        'sentence_date', lft.sentence_date,
                        'answer_date', lft.answer_date
                    )
                    ORDER BY lft.sentence_date DESC, lft.answer_date DESC
                ) AS new_apartments
            FROM 
                old_apart_data oa
                LEFT JOIN lft ON oa.affair_id = lft.affair_id
                where oa.affair_id = {apartment_id}
            GROUP BY 
                oa.affair_id,
                oa.house_address,
                oa.apart_number,
                oa.district,
                oa.municipal_district,
                oa.full_living_area,
                oa.total_living_area,
                oa.living_area,
                oa.room_count,
                oa.type_of_settlement
            ORDER BY 
                new_apartments;'''
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")
        print(query)
        result = await self._execute_query(query, {"apart_id": apartment_id})

        if not result:
            raise ValueError(f"Apartment with ID {apartment_id} not found")

        return dict(result[0]._mapping)

    async def get_house_address_with_room_count(self, apart_type):
        params = None
        if apart_type == "NewApartment":
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/AvaliableNewApartAddress.sql')
        elif apart_type == "OldApart":
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/AvaliableOldApartAddress.sql')  # Исправлена f-строка
        else:
            raise ValueError("ApartType not found")  # Исправлено исключение
            
        result = await self._execute_query(query, params=params)

        return result

