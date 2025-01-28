from sqlalchemy import text
from schema.apartment import ApartType
import logging

logger = logging.getLogger(__name__)


class ApartmentRepository:
    def __init__(self, db_manager):
        self.db_manager = db_manager  # Это sessionmaker

    async def _execute_query(self, query: str, params: dict) -> list[tuple]:
        """
        Выполнение запроса и возврат результата.
        """
        async with self.db_manager() as session:  # Создаем сессию
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

        table = "family_structure" if apart_type == "FamilyStructure" else "new_apart"
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

        table = "family_structure" if apart_type == "FamilyStructure" else "new_apart"
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

        table = "family_structure" if apart_type == "FamilyStructure" else "new_apart"
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
        where_clause = " AND ".join(conditions) if conditions else "rn = 1"

        # Формируем запрос в зависимости от типа квартир
        if apart_type == "FamilyStructure":
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
                        family_structure.notes,
                        family_apartment_needs_id,
                        ROW_NUMBER() OVER (PARTITION BY family_apartment_needs_id ORDER BY offer.sentence_date DESC, offer.answer_date DESC) AS rn
                    FROM
                        family_structure
                    LEFT JOIN
                        family_apartment_needs USING (affair_id)
                    LEFT JOIN
                        offer USING (family_apartment_needs_id)
                    LEFT JOIN
                        status ON offer.status_id = status.status_id
                )
                SELECT *
                FROM ranked_apartments
                WHERE {where_clause}
                ORDER BY full_living_area
            """
        else:
            query = f"""
                WITH ranked_apartments AS (
                    SELECT 
                        house_address, 
                        apart_number, 
                        district, 
                        municipal_district,
                        floor,
                        full_living_area,
                        total_living_area, 
                        living_area, 
                        room_count, 
                        type_of_settlement, 
                        status.status AS status, 
                        new_apart.notes, 
                        new_apart.new_apart_id,
                        ROW_NUMBER() OVER (PARTITION BY new_apart.new_apart_id ORDER BY offer.sentence_date DESC, offer.answer_date DESC) AS rn
                    FROM 
                        new_apart
                    LEFT JOIN 
                        offer USING (new_apart_id)
                    LEFT JOIN 
                        status ON offer.status_id = status.status_id
                )
                SELECT *
                FROM ranked_apartments
                WHERE {where_clause}
                ORDER BY full_living_area
            """

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
            query = f"""
                WITH old_apartment_list AS (
                    SELECT
                        na.new_apart_id,
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'house_address', fs.house_address,
                                'apart_number', fs.apart_number,
                                'district', fs.district,
                                'municipal_district', fs.municipal_district,
                                'full_living_area', fs.full_living_area,
                                'total_living_area', fs.total_living_area,
                                'living_area', fs.living_area,
                                'room_count', fs.room_count,
                                'type_of_settlement', fs.type_of_settlement,
                                'notes', o.notes,
                                'status', s.status,
                                'sentence_date', o.sentence_date :: DATE,
                                'answer_date', o.answer_date :: DATE
                            )
                        ) FILTER (WHERE fs.house_address IS NOT NULL OR fs.apart_number IS NOT NULL OR fs.district IS NOT NULL OR fs.municipal_district IS NOT NULL 
                        OR fs.full_living_area IS NOT NULL OR fs.total_living_area IS NOT NULL OR fs.living_area IS NOT NULL 
                        OR fs.room_count IS NOT NULL OR fs.type_of_settlement IS NOT NULL OR o.notes IS NOT NULL 
                        OR s.status IS NOT NULL OR o.sentence_date IS NOT NULL OR o.answer_date IS NOT NULL) AS old_apartments
                    FROM 
                        new_apart na
                    LEFT JOIN 
                        offer o USING (new_apart_id)
                    LEFT JOIN 
                        family_apartment_needs fan USING (family_apartment_needs_id)
                    LEFT JOIN 
                        family_structure fs USING (affair_id)
                    LEFT JOIN 
                        status s ON o.status_id = s.status_id
                    GROUP BY 
                        na.new_apart_id
                )
                SELECT 
                    na.new_apart_id,
                    na.house_address,
                    na.apart_number ,
                    na.district ,
                    na.municipal_district ,
                    na.full_living_area  ,
                    na.total_living_area ,
                    na.living_area ,
                    na.room_count ,
                    na.type_of_settlement,
                    na.notes ,
                    oal.old_apartments
                FROM 
                    new_apart na
                LEFT JOIN 
                    old_apartment_list oal ON na.new_apart_id = oal.new_apart_id
                WHERE
                    na.new_apart_id = {apartment_id}
                ORDER BY 
                    na.new_apart_id;
            """
        elif apart_type == "FamilyStructure":
            query = f"""
                WITH new_apartment_list AS (
                    SELECT 
                        o.family_apartment_needs_id,
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
                                'status', COALESCE(s.status, '?'),
                                'sentence_date', o.sentence_date :: DATE,
                                'answer_date', o.answer_date :: DATE
                            )
                        ) FILTER (WHERE na.house_address IS NOT NULL OR na.apart_number IS NOT NULL OR na.district IS NOT NULL OR na.municipal_district IS NOT NULL 
                        OR na.full_living_area IS NOT NULL OR na.total_living_area IS NOT NULL OR na.living_area IS NOT NULL 
                        OR na.room_count IS NOT NULL OR na.type_of_settlement IS NOT NULL OR na.notes IS NOT NULL 
                        OR s.status IS NOT NULL OR o.sentence_date IS NOT NULL OR o.answer_date IS NOT NULL) AS new_apartments
                    FROM 
                        offer o
                    LEFT JOIN 
                        new_apart na ON o.new_apart_id = na.new_apart_id
                    LEFT JOIN 
                        status s ON o.status_id = s.status_id
                    GROUP BY 
                        o.family_apartment_needs_id
                )
                SELECT 
                    fan.family_apartment_needs_id,
                    fs.house_address,
                    fs.apart_number,
                    fs.district,
                    fs.municipal_district,
                    fs.full_living_area,
                    fs.total_living_area,
                    fs.living_area,
                    fs.room_count,
                    fs.type_of_settlement,
                    nal.new_apartments
                FROM 
                    family_apartment_needs fan
                LEFT JOIN 
                    family_structure fs ON fan.affair_id = fs.affair_id
                LEFT JOIN 
                    new_apartment_list nal ON fan.family_apartment_needs_id = nal.family_apartment_needs_id
                WHERE
                    fan.family_apartment_needs_id = {apartment_id}
                ORDER BY 
                    fs.affair_id;
            """
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")

        result = await self._execute_query(query, {"apart_id": apartment_id})

        if not result:
            raise ValueError(f"Apartment with ID {apartment_id} not found")

        return dict(result[0]._mapping)

