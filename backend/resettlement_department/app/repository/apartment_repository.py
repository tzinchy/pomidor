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
                SELECT * FROM {table}
                LEFT JOIN family_apartment_needs USING (affair_id)
                LEFT JOIN offer USING (family_apartment_needs_id)
                LEFT JOIN status USING (status_id)
                WHERE house_address IN ({house_addresses_placeholders})
            """
        else:
            # Для других типов квартир используем стандартный запрос
            query_template = f"""
                SELECT * FROM {table}
                LEFT JOIN offer USING (new_apart_id)
                LEFT JOIN status USING (status_id)
                WHERE house_address IN ({house_addresses_placeholders})
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
            table = "public.new_apart"
            id_column = "new_apart_id"
        elif apart_type == "FamilyStructure":
            table = "public.family_structure"
            id_column = "affair_id"
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")

        # SQL-запрос
        query = f"""
            SELECT *
            FROM {table}
            WHERE {id_column} = :apart_id
        """

        result = await ApartmentRepository._execute_query(
            query, {"apart_id": apartment_id}
        )

        if not result:
            raise ValueError(f"Apartment with ID {apartment_id} not found in {table}")

        return dict(result[0]._mapping)
