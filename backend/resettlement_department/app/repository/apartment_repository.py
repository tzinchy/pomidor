from sqlalchemy import text
from repository.database import async_session_maker
from models.apartment import ApartType


class ApartmentRepository:
    @staticmethod
    async def _execute_query(query: str, params: dict) -> list[tuple]:
        """
        Выполнение запроса и возврат результата.
        """
        async with async_session_maker() as session:
            try:
                print(f"Executing query: {query}")
                print(f"Params: {params}")
                result = await session.execute(text(query), params)
                return result.fetchall()
            except Exception as e:
                print(f"Error executing query: {e}")
                raise

    @staticmethod
    def _build_placeholders(values: list[str], prefix: str) -> tuple[str, dict]:
        """
        Создать placeholders и параметры для подстановки.
        """
        placeholders = ", ".join(f":{prefix}_{i}" for i in range(len(values)))
        params = {f"{prefix}_{i}": value.strip() for i, value in enumerate(values)}
        return placeholders, params

    @staticmethod
    async def get_districts(apart_type: str) -> list[str]:
        """
        Получить уникальные районы.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        query = """
            SELECT DISTINCT district 
            FROM {table}
            order by district
        """
        table = (
            "public.family_structure"
            if apart_type == "FamilyStructure"
            else "public.new_apart"
        )

        # Формирование запроса
        query = query.format(table=table)
        result = await ApartmentRepository._execute_query(query, {})
        return [row[0] for row in result if row[0] is not None]

    @staticmethod
    async def get_municipal_district(
        apart_type: str, districts: list[str]
    ) -> list[str]:
        """
        Получить уникальные области по районам.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        query_template = """
            SELECT DISTINCT municipal_district
            FROM {table}
            WHERE district IN ({district_placeholders})
            order by municipal_district
        """
        table = (
            "public.family_structure"
            if apart_type == "FamilyStructure"
            else "public.new_apart"
        )

        # Генерация placeholders и параметров
        district_placeholders, params = ApartmentRepository._build_placeholders(
            districts, "district"
        )

        # Формирование запроса
        query = query_template.format(
            table=table, district_placeholders=district_placeholders
        )
        result = await ApartmentRepository._execute_query(query, params)
        return [row[0] for row in result if row[0] is not None]

    @staticmethod
    async def get_house_addresses(apart_type: str, areas: list[str]) -> list[str]:
        """
        Получить уникальные адреса домов по областям.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        query_template = """
            SELECT DISTINCT house_address
            FROM {table}
            WHERE municipal_district IN ({area_placeholders})
            order by house_address
        """
        table = (
            "public.family_structure"
            if apart_type == "FamilyStructure"
            else "public.new_apart"
        )

        # Генерация placeholders и параметров
        area_placeholders, params = ApartmentRepository._build_placeholders(
            areas, "area"
        )

        # Формирование запроса
        query = query_template.format(table=table, area_placeholders=area_placeholders)
        result = await ApartmentRepository._execute_query(query, params)
        return [row[0] for row in result if row[0] is not None]

    @staticmethod
    async def get_apartments(apart_type: str, house_addresses: list[str]) -> list[dict]:
        """
        Получаем все квартиры по адресам.
        """
        from datetime import datetime

        print(datetime.now())
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        # Выбор таблицы
        table = (
            "public.family_structure"
            if apart_type == "FamilyStructure"
            else "public.new_apart"
        )

        # Генерация placeholders и параметров
        house_addresses_placeholders, params = ApartmentRepository._build_placeholders(
            house_addresses, "house_address"
        )

        # Строим SQL-запрос
        if apart_type == "FamilyStructure":
            # Для "FamilyStructure" добавляем дополнительные LEFT JOIN
            query_template = f"""
                WITH ranked_apartments AS (
                    SELECT
                        house_address,
                        apart_number,
                        district,
                        municipal_district,
                        fio,
                        full_living_area,
                        total_living_area,
                        living_area,
                        room_count,
                        family_structure.type_of_settlement,
                        status.status,
                        family_structure.notes,
                        family_apartment_needs_id,
                        ROW_NUMBER() OVER (PARTITION BY family_apartment_needs_id ORDER BY offer.sentence_date, offer.answer_date DESC) AS rn
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
                WHERE house_address IN ({house_addresses_placeholders}) and rn = 1
                ORDER BY full_living_area
            """
        else:
            # Для других типов квартир используем стандартный запрос
            query_template = f"""
                WITH ranked_apartments AS (
                    SELECT 
                        house_address, 
                        apart_number, 
                        district, 
                        municipal_district, 
                        full_living_area,
                        total_living_area, 
                        living_area, 
                        room_count, 
                        type_of_settlement, 
                        status.status AS status, 
                        new_apart.notes, 
                        new_apart.new_apart_id,
                        ROW_NUMBER() OVER (PARTITION BY new_apart.new_apart_id ORDER BY offer.sentence_date, offer.answer_date DESC) AS rn
                    FROM 
                        public.new_apart
                    LEFT JOIN 
                        offer USING (new_apart_id)
                    LEFT JOIN 
                        status ON offer.status_id = status.status_id
                )
                SELECT *
                FROM ranked_apartments
                WHERE house_address IN ({house_addresses_placeholders}) and rn = 1
                order by full_living_area
            """

        # Выполнение запроса
        result = await ApartmentRepository._execute_query(query_template, params)

        print(datetime.now())
        # Преобразуем результат в список словарей
        return [dict(row._mapping) for row in result]

    @staticmethod
    async def get_apartment_by_id(apartment_id: int, apart_type: str) -> dict:
        """
        Получить всю информацию о квартире по ID, учитывая разное имя столбца для разных таблиц.
        """

        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        # Определяем таблицу и имя столбца для ID
        if apart_type == "NewApartment":
            # SQL-запрос
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
                        public.new_apart na
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
                    public.new_apart na
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
                    fan.family_apartment_needs_id = {apartment_id} -- Фильтр по family_apartment_needs_id
                ORDER BY 
                    fs.affair_id;
            """
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")

        

        result = await ApartmentRepository._execute_query(
            query, {"apart_id": apartment_id}
        )

        if not result:
            raise ValueError(f"Apartment with ID {apartment_id} not found")

        return dict(result[0]._mapping)
