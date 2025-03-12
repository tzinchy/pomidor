from sqlalchemy import text
from schema.apartment import ApartType
import logging
from utils.sql_reader import read_sql_query
from core.config import RECOMMENDATION_FILE_PATH
from handlers.httpexceptions import SomethingWrong
from sqlalchemy.exc import SQLAlchemyError

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
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                raise

    async def get_municipal_district(
        self, apart_type: str, districts: list[str]
    ) -> list[str]:
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
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                raise

    async def get_house_addresses(
        self, apart_type: str, municipal_districts: list[str]
    ) -> list[str]:
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
            except Exception as error:
                logger.error(f"Error executing query: {error}")
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
        area_type: str = "full_living_area",
        is_queue: bool = None,
        is_private: bool = None,
    ) -> list[dict]:
        """
        Получаем все квартиры с учетом опциональных фильтров.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")
        if area_type not in ["full_living_area", "total_living_area", "living_area"]:
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

        if is_queue is not None and apart_type == ApartType.OLD:
            conditions.append("is_queue != 0")

        if is_private is not None and apart_type == ApartType.NEW:
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

        # Формируем запрос в зависимости от типа квартир
        if apart_type == "OldApart":
            print(conditions)
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/OldApartTable.sql")
        else:
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/NewApartTable.sql")

        query = f"{query} WHERE {where_clause}"
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                logger.info(f"Params: {params}")
                result = await session.execute(text(query), params)
                return [dict(row._mapping) for row in result]
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                raise

    async def get_apartment_by_id(self, apart_id: int, apart_type: str) -> dict:
        """
        Получить всю информацию о квартире по ID.
        """
        if apart_type not in ApartType:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        query_params = {"apart_id": apart_id}

        if apart_type == "NewApartment":
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/NewApartById.sql")
        elif apart_type == "OldApart":
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/OldApartById.sql")
        else:
            raise ValueError(f"Unsupported apartment type: {apart_type}")
        print(query)
        async with self.db() as session:
            try:
                logger.info(f"Executing query: {query}")
                result = await session.execute(text(query), query_params)
                data = result.fetchone()
                if not data:
                    raise ValueError(f"Apartment with ID {apart_id} not found")
                return dict(data._mapping)
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                raise SomethingWrong

    async def get_house_address_with_room_count(self, apart_type):
        if apart_type == "NewApartment":
            query = read_sql_query(
                f"{RECOMMENDATION_FILE_PATH}/AvaliableNewApartAddress.sql"
            )
        elif apart_type == "OldApart":
            query = read_sql_query(
                f"{RECOMMENDATION_FILE_PATH}/AvaliableOldApartAddress.sql"
            )
        else:
            raise ValueError("Invalid apartment type")

        async with self.db() as session:
            try:
                result = await session.execute(text(query))
                return result.fetchall()
            except Exception as e:
                logger.error(f"Error executing query: {e}")
                raise SomethingWrong

    async def switch_apartment(self, first_apart_id, second_apart_id):
        query = "SELECT swap_new_aparts(:first_apart_id, :second_apart_id)"
        params = {
            "first_apart_id": int(first_apart_id),
            "second_apart_id": int(second_apart_id),
        }
        async with self.db() as session:
            try:
                result = await session.execute(text(query), params)
                await session.commit()

                rows = result.fetchall()
                if rows:
                    serialized_result = [row._asdict() for row in rows] 
                    return serialized_result[0]
                else:
                    # Если результат пуст, возвращаем сообщение
                    return {"message": "No rows affected"}

            except Exception as e:
                logger.error(f"Error switching apartments: {e}")
                raise SomethingWrong

    async def manual_matching(self, old_apart_id, new_apart_id):
        try:
            async with self.db() as session:
                # Проверка существования записи
                check_query = text("""
                    SELECT EXISTS (
                        SELECT 1
                        FROM public.offer
                        WHERE affair_id = :old_apart_id
                    );
                """)
                result = await session.execute(
                    check_query, {"old_apart_id": old_apart_id}
                )
                record_exists = result.scalar()

                if record_exists:
                    # Обновление записи
                    update_query = text(read_sql_query(f'{RECOMMENDATION_FILE_PATH}/UpdateOfferStatus.sql'))
                    await session.execute(update_query, {"status" : "Отказ", "old_apart_id": old_apart_id})
                    print(
                        f"Обновлена последняя запись для old_apart_id {old_apart_id}: {new_apart_id}"
                    )

                # Вставка новой записи
                insert_query = text("""
                    INSERT INTO public.offer (affair_id, new_aparts, status_id)
                    VALUES (:old_apart_id, jsonb_build_object((:new_apart_id)::int, jsonb_build_object('status_id', 7)), 7);
                """)
                await session.execute(
                    insert_query,
                    {"old_apart_id": old_apart_id, "new_apart_id": new_apart_id},
                )
                print(
                    f"Вставлена новая запись для old_apart_id {old_apart_id}: {new_apart_id}"
                )
                await session.commit()
        except SQLAlchemyError as e:
            print(f"Ошибка при обработке old_apart_id {old_apart_id}: {e}")
            await session.rollback()
            raise SomethingWrong

        return "success"

    async def get_void_aparts_for_apartment(self, apart_id):
        async with self.db() as session:
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/VoidAparts.sql")
            result = await session.execute(text(query), {"apart_id": apart_id})
            return [dict(row._mapping) for row in result]

    async def cancell_matching_apart(self, apart_id, apart_type):
        async with self.db() as session:
            try:
                if apart_type == ApartType.OLD:
                    result = await session.execute(
                        text("DELETE FROM offer WHERE affair_id = :apart_id"),
                        {"apart_id": apart_id},
                    )
                    await session.commit()
                    return result
                else:
                    result = await session.execute(
                        text("""
                    WITH new_apart_in_offer AS (
                        SELECT offer_id
                            FROM offer,
                            jsonb_each(new_aparts)
                            where (key)::int = :apart_id)
                    DELETE FROM offer
                    WHERE offer_id IN (SELECT offer_id FROM new_apart_in_offer)"""),
                        {"apart_id": apart_id},
                    )
                    await session.commit()
                    return result
            except Exception as error:
                print(error)
                raise SomethingWrong

    async def update_status_for_apart(self, apart_id, status, apart_type):
        async with self.db() as session:
            try:
                if apart_type == ApartType.OLD:

                    query = text(read_sql_query(f'{RECOMMENDATION_FILE_PATH}/UpdateOfferStatus.sql'))
                    result = await session.execute(
                        query, {"status": status, "apart_id": apart_id}
                    )
                    await session.commit()
                    return result
            except SQLAlchemyError as error:
                print(error)
                await session.rollback()
                raise SomethingWrong(
                    "An error occurred while updating the apartment status."
                )
    
    async def set_private_for_new_aparts(self, new_apart_ids, status : bool = True):
        async with self.db() as session:
            try: 
                await session.execute(text('UPDATE new_apart SET is_private = :status WHERE new_apart_id IN (:new_apart_ids)'), {'new_apart_ids' : new_apart_ids, 'status' : status})
                await session.commit() 
            except Exception as error: 
                print(error)
                raise SomethingWrong
            
   
