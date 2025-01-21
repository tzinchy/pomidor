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

    async def get_house_addresses(apart_type: str, areas: list[str], district: list[str] = None) -> list[str]:
        """
        Получить уникальные адреса домов по областям и районам (если указаны)
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        # Базовый шаблон запроса
        query_template = """
            SELECT DISTINCT house_address
            FROM {table}
            WHERE municipal_district IN ({area_placeholders})
            {district_clause}
            ORDER BY house_address
        """

        # Определяем таблицу
        table = (
            "public.family_structure" 
            if apart_type == "FamilyStructure" 
            else "public.new_apart"
        )

        # Строим условия для районов
        district_clause = ""
        district_params = []
        
        if district:
            district_placeholders, district_params = ApartmentRepository._build_placeholders(
                district, "district"
            )
            district_clause = f"AND district IN ({district_placeholders})"

        # Строим условия для областей
        area_placeholders, area_params = ApartmentRepository._build_placeholders(
            areas, "area"
        )

        # Объединяем параметры
        all_params = area_params + district_params

        # Формируем итоговый запрос
        final_query = query_template.format(
            table=table,
            area_placeholders=area_placeholders,
            district_clause=district_clause
        )

        # Выполняем запрос
        result = await ApartmentRepository._execute_query(final_query, all_params)
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
                SELECT house_address, apart_number, district, municipal_district, fio, full_living_area,
                total_living_area, living_area, room_count, family_structure.type_of_settlement, status.status, family_structure.notes, family_apartment_needs_id
                 FROM {table}
                LEFT JOIN family_apartment_needs USING (affair_id)
                LEFT JOIN offer USING (family_apartment_needs_id)
                LEFT JOIN status on offer.status_id = status.status_id
                WHERE house_address IN ({house_addresses_placeholders})
                order by full_living_area
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
                        ROW_NUMBER() OVER (PARTITION BY new_apart.new_apart_id ORDER BY offer.sentence_date DESC) AS rn
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
                                'status', COALESCE(s.status, '?'),
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
                WITH old_apartment_list AS (
                    SELECT 
                        fan.family_apartment_needs_id,
                        fan.affair_id,
                        JSON_AGG(
                            JSON_BUILD_OBJECT(
                                'address', fas.house_address,
                                'apartment_number', fas.apart_number,
                                'district', fas.district,
                                'municipal_district', fas.municipal_district,
                                'full_living_area', fas.full_living_area,
                                'total_living_area', fas.total_living_area,
                                'living_area', fas.living_area,
                                'room_count', fas.room_count,
                                'type_of_settlement', fas.type_of_settlement,
                                'offer_notes', o.notes,
                                'status', COALESCE(s.status, '?'),
                                'sentence_date', o.sentence_date::date,
                                'answer_date', o.answer_date::date
                            )
                        ) FILTER (
                            WHERE fas.house_address IS NOT NULL 
                            OR fas.apart_number IS NOT NULL 
                            OR fas.district IS NOT NULL 
                            OR fas.municipal_district IS NOT NULL 
                            OR fas.full_living_area IS NOT NULL 
                            OR fas.total_living_area IS NOT NULL 
                            OR fas.living_area IS NOT NULL 
                            OR fas.room_count IS NOT NULL 
                            OR fas.type_of_settlement IS NOT NULL 
                            OR o.notes IS NOT NULL 
                            OR s.status IS NOT NULL 
                            OR o.sentence_date IS NOT NULL 
                            OR o.answer_date IS NOT NULL
                        ) AS new_apartments
                    FROM 
                        public.family_apartment_needs fan
                    LEFT JOIN 
                        offer o ON fan.family_apartment_needs_id = o.family_apartment_needs_id
                    LEFT JOIN  
                        family_structure fas ON fan.affair_id = fas.affair_id -- Correctly joining with fas
                    LEFT JOIN 
                        status s ON o.status_id = s.status_id
                    GROUP BY 
                        fan.family_apartment_needs_id, fan.affair_id -- Including fan.affair_id in GROUP BY
                )
                SELECT 
                    fan.family_apartment_needs_id,
                    fas.house_address,
                    fas.apart_number,
                    fas.district,
                    fas.municipal_district,
                    fas.full_living_area,
                    fas.total_living_area,
                    fas.living_area,
                    fas.room_count,
                    fas.type_of_settlement,
                    nal.new_apartments
                FROM 
                    public.family_apartment_needs fan
                LEFT JOIN 
                    old_apartment_list nal ON fan.family_apartment_needs_id = nal.family_apartment_needs_id -- Joining correctly with nal
                LEFT JOIN 
                    public.family_structure fas ON fas.affair_id = fan.affair_id
                where fas.affair_id = {apartment_id}
            """
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")

        

        result = await ApartmentRepository._execute_query(
            query, {"apart_id": apartment_id}
        )

        if not result:
            raise ValueError(f"Apartment with ID {apartment_id} not found")

        return dict(result[0]._mapping)
