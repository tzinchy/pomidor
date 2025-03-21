from sqlalchemy import text
from schema.apartment import ApartTypeSchema
import logging
from utils.sql_reader import read_sql_query
from core.config import RECOMMENDATION_FILE_PATH
from handlers.httpexceptions import SomethingWrong
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional

logger = logging.getLogger(__name__)


class ApartmentRepository:
    def __init__(self, session_maker):
        self.db = session_maker

    async def get_districts(self, apart_type: str) -> list[str]:
        """
        Получить уникальные районы.
        """
        if apart_type not in ApartTypeSchema:
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
        if apart_type not in ApartTypeSchema:
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
        if apart_type not in ApartTypeSchema:
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
        if apart_type not in ApartTypeSchema:
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

                return [row._mapping for row in result]
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                print(error)
                raise SomethingWrong

    async def get_apartment_by_id(self, apart_id: int, apart_type: str) -> dict:
        if apart_type not in ApartTypeSchema:
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
                data = result.fetchall()
                if not data:
                    raise ValueError(f"Apartment with ID {apart_id} not found")

                return [row._mapping for row in data][0]
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                print(error)
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

    async def manual_matching(self, apart_id, new_apart_ids):
        try:
            async with self.db() as session:
                # Проверяем существующие согласованные квартиры
                check_approved_query = text("""
                    SELECT jsonb_object_agg(key::text, value)
                    FROM (
                        SELECT key, value 
                        FROM offer, jsonb_each(new_aparts)
                        WHERE affair_id = :apart_id
                        AND (value->>'status_id')::int = 1
                    ) approved_aparts;
                """)

                result = await session.execute(
                    check_approved_query, {"apart_id": apart_id}
                )
                approved_aparts = result.scalar() or {}

                # Объединяем существующие согласованные квартиры с новыми
                all_apart_ids = list(approved_aparts.keys()) + new_apart_ids

                if not all_apart_ids:
                    raise ValueError("Нет квартир для добавления")

                # Обновляем предыдущий офер только если нет согласованных квартир
                if not approved_aparts:
                    update_query = text(
                        read_sql_query(
                            f"{RECOMMENDATION_FILE_PATH}/UpdateOfferStatus.sql"
                        )
                    )
                    await session.execute(
                        update_query, {"status": "Отказ", "apart_id": apart_id}
                    )

                # Создаем JSONB объект для новых квартир
                insert_query = text("""
                    INSERT INTO public.offer (affair_id, new_aparts, status_id)
                    VALUES (
                        :old_apart_id,
                        jsonb_object(
                            (:apart_ids)::text[],
                            (SELECT array_agg(jsonb_build_object('status_id', 7)) 
                            FROM unnest((:apart_ids)::text[]))
                        ),
                        7
                    );
                """)

                await session.execute(
                    insert_query, {"old_apart_id": apart_id, "apart_ids": all_apart_ids}
                )

                await session.commit()
                return "success"

        except SQLAlchemyError as e:
            print(f"Ошибка при обработке old_apart_id {apart_id}: {e}")
            await session.rollback()
            raise SomethingWrong

    async def get_void_aparts_for_apartment(self, apart_id):
        async with self.db() as session:
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/VoidAparts.sql")
            result = await session.execute(text(query), {"apart_id": apart_id})
            return [row._mapping for row in result]

    async def cancell_matching_apart(self, apart_id, apart_type):
        async with self.db() as session:
            try:
                if apart_type == ApartTypeSchema.OLD:
                    result = await session.execute(
                        text(
                            "DELETE FROM offer WHERE affair_id = :apart_id AND offer_id = (select max(offer_id) from offer where affair_id = :apart_id)"
                        ),
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
                            WHERE offer_id = (SELECT MAX(offer_id) FROM new_apart_in_offer);"""),
                        {"apart_id": apart_id},
                    )
                    await session.commit()
                    return result
            except Exception as error:
                print(error)
                raise SomethingWrong

    async def update_status_for_apart(
        self, apart_id, new_apartment_id, status, apart_type
    ):
        async with self.db() as session:
            try:
                if apart_type == ApartTypeSchema.OLD:
                    query = text(
                        read_sql_query(
                            f"{RECOMMENDATION_FILE_PATH}/UpdateOfferStatusForNewApart.sql"
                        )
                    )
                    result = await session.execute(
                        query,
                        {
                            "status": status,
                            "apart_id": apart_id,
                            "new_apart_id": str(new_apartment_id),
                        },
                    )
                    await session.commit()
                    return result
            except SQLAlchemyError as error:
                print(error)
                await session.rollback()
                raise SomethingWrong(
                    "An error occurred while updating the apartment status."
                )

    async def set_private_for_new_aparts(self, new_apart_ids, status: bool = True):
        async with self.db() as session:
            try:
                # Проверяем, что new_apart_ids не пустой
                if not new_apart_ids:
                    raise ValueError("The list of apartment IDs is empty.")

                # Формируем строку с плейсхолдерами для каждого ID
                placeholders = ", ".join(
                    [":id_" + str(i) for i in range(len(new_apart_ids))]
                )

                # Формируем словарь с параметрами
                params = {"status": status}
                params.update({f"id_{i}": id for i, id in enumerate(new_apart_ids)})

                # Используем параметризованный запрос для безопасности
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

    async def set_decline_reason(
        self,
        apartment_id,
        new_apart_id,
        min_floor: Optional[int] = None,
        max_floor: Optional[int] = None,
        unom: Optional[str] = None,
        entrance: Optional[str] = None,
        apartment_layout: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        async with self.db() as session:
            try:
                # Вставляем данные в таблицу decline_reason
                insert_query = text("""
                    INSERT INTO public.decline_reason 
                    (min_floor, max_floor, unom, entrance, apartment_layout, notes)
                    VALUES (:min_floor, :max_floor, :unom, :entrance, :apartment_layout, :notes)
                    RETURNING decline_reason_id;
                """)
                result = await session.execute(
                    insert_query,
                    {
                        "min_floor": min_floor,
                        "max_floor": max_floor,
                        "unom": unom,
                        "entrance": entrance,
                        "apartment_layout": apartment_layout,
                        "notes": notes,
                    },
                )
                decline_reason_id = result.scalar()

                # Обновляем статус в таблице offer
                update_query = text("""
                    WITH updated_data AS (
                        SELECT
                            offer_id,
                            new_apart_id,
                            jsonb_set(
                                jsonb_set(
                                    new_aparts->(new_apart_id::text),
                                    '{status_id}',
                                    to_jsonb((SELECT status_id FROM status WHERE status = :status))
                                ),
                                '{decline_reason_id}',
                                to_jsonb((:declined_reason_id)::int)
                            ) AS updated_value
                        FROM
                            offer,
                            jsonb_each(new_aparts) AS each(new_apart_id, value)
                        WHERE
                            offer_id = (SELECT MAX(offer_id) FROM offer where affair_id = :apart_id) 
                            AND new_apart_id::text = (:new_apart_id)::text 
                            AND affair_id = :apart_id
                    )
                    UPDATE offer
                    SET 
                        new_aparts = jsonb_set(
                            new_aparts,
                            ARRAY[updated_data.new_apart_id::text],
                            updated_data.updated_value
                        ),
                        status_id = (SELECT status_id FROM status WHERE status = :status)
                    FROM updated_data
                    WHERE offer.offer_id = updated_data.offer_id;
                """)
                await session.execute(
                    update_query,
                    {
                        "status": "Отказ",
                        "apart_id": apartment_id,
                        "declined_reason_id": decline_reason_id,
                        "new_apart_id": str(new_apart_id),
                    },
                )

                await session.commit()
                return {'status' : 'done'}
            except Exception as error:
                print(error)
                await session.rollback()
                raise SomethingWrong

    async def set_notes(self, apart_id: int, notes: str, apart_type: str):
        async with self.db() as session:
            try:
                if apart_type == ApartTypeSchema.OLD:
                    await session.execute(
                        text("""
                        UPDATE old_apart SET notes = :notes 
                        WHERE affair_id = :apart_id
                        """),
                        {"notes": notes, "apart_id": apart_id},
                    )
                elif apart_type == ApartTypeSchema.NEW:
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
                raise SomethingWrong

    async def get_decline_reason(self, decline_reason_id: int):
        async with self.db() as session:
            result = await session.execute(
                (
                    text("""SELECT min_floor, max_floor, unom, entrance, notes, apartment_layout FROM public.decline_reason
                                                WHERE decline_reason_id = :decline_reason_id 
            """)
                ),
                {"decline_reason_id": decline_reason_id},
            )
            result = result.fetchone() 
            return result._mapping

    async def update_decline_reason(
        self,
        decline_reason_id: int,
        min_floor: Optional[int] = None,
        max_floor: Optional[int] = None,
        unom: Optional[str] = None,
        entrance: Optional[str] = None,
        apartment_layout: Optional[str] = None,
        notes: Optional[str] = None,
    ):
        async with self.db() as session:
            try:
                # Собираем параметры, исключая None
                params = {
                    "min_floor": min_floor,
                    "max_floor": max_floor,
                    "unom": unom,
                    "entrance": entrance,
                    "apartment_layout": apartment_layout,
                    "notes": notes,
                }
                filtered_params = {
                    key: value for key, value in params.items() if value is not None
                }

                if not filtered_params:
                    return {"status": "no_changes"} 

                set_clause = ", ".join(
                    [f"{key} = :{key}" for key in filtered_params.keys()]
                )
                filtered_params["cancell_reason_id"] = (
                    decline_reason_id 
                )

                update_query = text(f"""
                    UPDATE public.decline_reason 
                    SET {set_clause}
                    WHERE decline_reason_id = :cancell_reason_id
                """)

                await session.execute(update_query, filtered_params)
                await session.commit()
                return {"status": "done"}
            except Exception as e:
                await session.rollback()
                raise Exception(f"Something went wrong: {e}")
