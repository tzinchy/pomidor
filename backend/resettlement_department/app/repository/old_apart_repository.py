import json
from typing import List, Optional

from core.config import RECOMMENDATION_FILE_PATH
from schema.apartment import ApartType
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
from utils.sql_reader import async_read_sql_query


class OldApartRepository:
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_districts(self, user_districts: Optional[list[str]] = None) -> list[str]:
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

    async def get_municipal_district(self, districts: list[str] = None) -> list[str]:
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

    async def get_house_addresses(
        self, municipal_districts: list[str] = None, district : list[str] = None,
    ) -> list[str]:
        params = {}
        query = "SELECT DISTINCT house_address FROM old_apart WHERE 1=1"
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
                    FROM old_apart
                    GROUP BY district
                ) AS subquery;
            """)
            )

            rows = result.fetchall()
            if rows:
                return rows[0]._mapping["result"]
            return {}

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
        statuses: List[str] = None,
        fio : str = None,
        stage: List[str] = None,
        otsel_type: List[str] = None
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
        if statuses:
            statuses = [
                f"'{i}'" for i in statuses
            ]  # Добавляем кавычки вокруг каждого значения
            print(statuses)
            conditions.append(f"status IN ({', '.join(statuses)})")
        if fio: 
            conditions.append(f"fio like '%{fio}%'")
        if stage:
            stage = [
                f"'{i}'" for i in stage
            ]  # Добавляем кавычки вокруг каждого значения
            print(stage)
            conditions.append(f' "buildingRelocationStatus" IN ({", ".join(stage)})') 
        if otsel_type:
            otsel_type = [
                f"'{i}'" for i in otsel_type
            ]  # Добавляем кавычки вокруг каждого значения
            print(otsel_type)
            conditions.append(f' type IN ({", ".join(otsel_type)})')


        where_clause = " AND ".join(conditions)

        query = await async_read_sql_query(
            f"{RECOMMENDATION_FILE_PATH}/OldApartTable.sql"
        )

        query = f"{query} WHERE {where_clause}"
        print(query)
        async with self.db() as session:
            result = await session.execute(text(query), params)
            clear_result = [row._mapping for row in result]
            print(len(clear_result))
            return clear_result

    async def get_apartment_by_id(self, apart_id: int) -> dict:
        params = {"apart_id": apart_id}

        query = await async_read_sql_query(
            f"{RECOMMENDATION_FILE_PATH}/OldApartById.sql"
        )

        async with self.db() as session:
            result = await session.execute(text(query), params)
            data = result.fetchall()
            if not data:
                raise ValueError(f"Apartment with ID {apart_id} not found")
            result = [row._mapping for row in data][0]
            return result

    async def get_house_address_with_room_count(self):
        query = await async_read_sql_query(
            f"{RECOMMENDATION_FILE_PATH}/AvaliableOldApartAddress.sql"
        )
        print(query)
        async with self.db() as session:
            result = await session.execute(text(query))
            return result.fetchall()

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
                    serialized_result = [row._mapping for row in rows]
                    return serialized_result[0]
                else:
                    return {"message": "No rows affected"}
            except Exception as error:
                session.rollback()
                raise error

    async def manual_matching(self, old_apart_id, new_apart_ids):
        async with self.db() as session:
            try:
                aparts = {}
                type_of_user = await session.execute(
                    text(
                        """SELECT is_queue FROM old_apart WHERE affair_id = :old_apart_id LIMIT 1;"""
                    ),
                    {"old_apart_id": old_apart_id},
                )
                is_queue = type_of_user.fetchone()[0]
                if is_queue == 0:
                    if len(new_apart_ids) != 1:
                        session.rollback()
                        raise Exception
                print("а выполнение уже тут")
                check_exist = await session.execute(
                    text("""
                    SELECT 1 FROM offer WHERE affair_id = :old_apart_id LIMIT 1;
                """),
                    {"old_apart_id": old_apart_id},
                )

                if check_exist.fetchone() is not None:
                    check_approved_query = text("""
                        SELECT jsonb_object_agg(key::text, value) 
                        FROM (
                            SELECT key, value 
                            FROM offer, jsonb_each(new_aparts)
                            WHERE affair_id = :apart_id
                            AND (value->>'status_id')::int = 1 and offer_id = (select max(offer_id) from offer where affair_id = :apart_id)
                        ) approved_aparts;
                    """)

                    result = await session.execute(
                        check_approved_query, {"apart_id": old_apart_id}
                    )
                    aparts = result.scalar() or {}
                    await session.execute(
                        text("""
                        WITH last_offer AS (
                            SELECT offer_id 
                            FROM offer 
                            WHERE affair_id = :apart_id 
                            ORDER BY offer_id DESC 
                            LIMIT 1
                        )
                        UPDATE offer 
                        SET status_id = 2 
                        WHERE offer_id = (SELECT offer_id FROM last_offer);
                    """),
                        {"apart_id": old_apart_id},
                    )

                for id in new_apart_ids:
                    aparts[str(id)] = {"status_id": 7}

                aparts_json = json.dumps(aparts)

                await session.execute(
                    text("""
                    INSERT INTO offer (affair_id, new_aparts, status_id) 
                    VALUES (:apart_id, (:aparts)::jsonb, 7);
                """),
                    {"apart_id": old_apart_id, "aparts": aparts_json},
                )

                await session.commit()
                return {"status": "done"}
            except Exception as error:
                await session.rollback()
                raise error

    async def get_void_aparts_for_apartment(self, apart_id):
        async with self.db() as session:
            query = await async_read_sql_query(
                f"{RECOMMENDATION_FILE_PATH}/VoidAparts.sql"
            )
            result = await session.execute(text(query), {"apart_id": apart_id})
            return [row._mapping for row in result]

    async def cancell_matching_apart(self, apart_id):
        async with self.db() as session:
            try:
                result = await session.execute(
                    text(
                        "DELETE FROM offer WHERE affair_id = :apart_id AND offer_id = (select max(offer_id) from offer where affair_id = :apart_id)"
                    ),
                    {"apart_id": apart_id},
                )
                await session.commit()
                return result
            except Exception as error:
                session.rollback()
                raise error

    async def validate_apart_status(self, apart_id : int, new_apart_id : int):
        async with self.db() as session:
                query = text('''
                    select affair_id, new_apart.status_id as status_id FROM offer, jsonb_each(new_aparts)
                    join new_apart ON KEY::bigint = new_apart_id
                    WHERE KEY::bigint = :new_apart_id
                    ORDER BY offer_id DESC
                    limit 1
                ''')
                
                pre_res = await session.execute(query, {'new_apart_id': new_apart_id})
                is_freedom = pre_res.fetchall()[0]
                print(is_freedom)
                offer_affair_id, new_apart_status = is_freedom
            
                return new_apart_status == 11 or offer_affair_id == apart_id
        
    async def update_status_for_apart(self, apart_id, new_apart_id, status):
        async with self.db() as session:
            try:
                query = text(
                    await async_read_sql_query(
                        f"{RECOMMENDATION_FILE_PATH}/UpdateOfferStatusForNewApart.sql"
                    )
                )
                result = await session.execute(
                    query,
                    {
                        "status": status,
                        "apart_id": apart_id,
                        "new_apart_id": str(new_apart_id),
                    },
                )
                print(result.rowcount)
                if result.rowcount == 0:
                    return {'status': 'Не удалось обновить статус: запись не найдена', 'error': True}
                await session.commit()
                print('update status_for_apart done')
                return {'status': 'Статус успешно обновлен', 'error': False}

            except Exception as error:
                await session.rollback()
                raise error
        
    async def set_decline_reason(
        self,
        apart_id,
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

                update_query = text("""
                    WITH updated_data AS (
                        SELECT
                            offer_id,
                            new_apart_id,
                            jsonb_set(
                                new_aparts->(new_apart_id::text),
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
                        )
                    FROM updated_data
                    WHERE offer.offer_id = updated_data.offer_id;
                """)
                await session.execute(
                    update_query,
                    {
                        "apart_id": apart_id,
                        "declined_reason_id": decline_reason_id,
                        "new_apart_id": str(new_apart_id),
                    },
                )

                await session.commit()
                return {"status": "done"}
            except Exception as error:
                await session.rollback()
                raise error

    async def set_notes(self, apart_ids: list[int], notes: str, rsm_note):
        async with self.db() as session:
            try:
                placeholder = ",".join(map(str, apart_ids))
                await session.execute(
                    text(f"""
                    UPDATE old_apart 
                    SET rsm_notes = :rsm_note,
                        notes = :notes
                    WHERE affair_id IN ({placeholder})
                    """),
                    {"rsm_note": rsm_note, "notes": notes},
                )
                await session.commit()
                return {"status": "done"}
            except Exception as error:
                session.rollback()
                raise error

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

                set_clause = ", ".join([
                    f"{key} = :{key}" for key in filtered_params.keys()
                ])
                filtered_params["decline_reason_id"] = decline_reason_id

                update_query = text(f"""
                    UPDATE public.decline_reason 
                    SET {set_clause}
                    WHERE decline_reason_id = :decline_reason_id
                """)

                await session.execute(update_query, filtered_params)
                await session.commit()
                return {"status": "done"}
            except Exception as error:
                await session.rollback()
                raise error

    async def set_status_for_many_old_apart(
        self, old_apart_ids: List[int], status: str
    ):
        async with self.db() as session:
            try:
                affair_ids = ", ".join(map(str, old_apart_ids))
                await session.execute(
                    text(f"""
                        WITH get_status_id AS (
                            SELECT status_id FROM status WHERE status = :status
                        ),
                        all_affairs AS (
                            SELECT unnest(ARRAY[{affair_ids}])::int AS affair_id
                        ),
                        with_offers AS (
                            SELECT DISTINCT o.affair_id
                            FROM offer o
                            WHERE o.affair_id IN (SELECT affair_id FROM all_affairs) and ((select status_id from get_status_id) not in (14))
                        ),
                        without_offers AS (
                            SELECT a.affair_id
                            FROM all_affairs a
                            WHERE NOT EXISTS (
                                SELECT 1 FROM offer o 
                                WHERE o.affair_id = a.affair_id
                            )
                            AND EXISTS (
                                SELECT 1 FROM old_apart oa 
                                WHERE oa.affair_id = a.affair_id
                            )
                        ),
                        latest_offers AS (
                            SELECT MAX(offer_id) as offer_id, affair_id
                            FROM offer
                            WHERE affair_id IN (SELECT affair_id FROM with_offers)
                            GROUP BY affair_id
                        ),
                        update_offers AS (
                            UPDATE offer
                            SET
                                status_id = (SELECT status_id FROM get_status_id),
                                new_aparts = CASE 
                                    WHEN new_aparts IS NOT NULL AND new_aparts != '{{}}'::jsonb THEN (
                                        SELECT COALESCE(
                                            jsonb_object_agg(
                                                key, 
                                                jsonb_set(
                                                    value, 
                                                    '{{status_id}}', 
                                                    to_jsonb((SELECT status_id FROM get_status_id))
                                                )
                                            ), 
                                            '{{}}'::jsonb
                                        )
                                        FROM jsonb_each(COALESCE(new_aparts, '{{}}'::jsonb))
                                    )
                                    ELSE new_aparts
                                END,
                                updated_at = NOW()
                            FROM latest_offers
                            WHERE offer.offer_id = latest_offers.offer_id
                            RETURNING 1
                        ),
                        update_old_aparts AS (
                            UPDATE old_apart 
                            SET 
                                status_id = (SELECT status_id FROM get_status_id),
                                updated_at = NOW()
                            WHERE affair_id IN (SELECT affair_id FROM without_offers)
                            RETURNING 1
                        )
                        SELECT 
                            (SELECT count(*) FROM update_offers) AS offers_updated,
                            (SELECT count(*) FROM update_old_aparts) AS old_aparts_updated;
                    """),
                    {"status": status},
                )
                await session.commit()
            except Exception as e:
                await session.rollback()
                raise e

    async def set_special_needs_for_many(
        self, old_apart_ids: List[int], is_special_needs_marker: int
    ):
        """
        Обновляет поле is_special_needs_marker у old_apart
        """
        async with self.db() as session:
            try:
                affair_ids = ", ".join(map(str, old_apart_ids))
                result = await session.execute(
                    text(f"""
                        UPDATE public.old_apart
                        SET is_special_needs_marker=:is_special_needs_marker
                        WHERE affair_id IN ({affair_ids})
                    """),
                    {"is_special_needs_marker": is_special_needs_marker},
                )
                await session.commit()
                return result.rowcount
            except Exception as e:
                await session.rollback()
                raise e

    async def get_excel_old_apart(self):
        query = text("""SELECT * FROM public.old_apart
                     JOIN status USING (status_id)""")
        results_list = []
        column_names = []

        async with self.db() as session:
            result_proxy = await session.execute(query)
            column_names = list(result_proxy.keys())
            results_list = result_proxy.all()
        return results_list, column_names

    async def get_current_table(self, apart_ids : list[int]):
        async with self.db() as session: 
            apart_ids = ', '.join(list(map(str,apart_ids)))
            result = await session.execute(text(f'''select 
                    old_apart.affair_id as "ID дела", 
                    old_apart.kpu_number as "Номер КПУ",
                    old_apart.fio as "ФИО",
                    old_apart.people_in_family as "Количество членов семьи",
                    old_apart.category as "Категория", 
                    old_apart.cad_num as "Кадастровый номер",
                    old_apart.district as "КПУ: Район",
                    old_apart.municipal_district as "КПУ: Муниципальный район",
                    old_apart.house_address as "КПУ: Адрес",
                    old_apart.room_count as "КПУ: Количество комнат", 
                    old_apart."floor" as "КПУ: Этаж",
                    old_apart.total_living_area as "КПУ: Общая площадь",
                    old_apart.full_living_area as "КПУ: Полная жилая площадь",
                    old_apart.living_area as "КПУ: Жилая площадь", 
                    CASE 
                        WHEN old_apart.is_special_needs_marker = 1 THEN 'Да'
                        WHEN old_apart.is_special_needs_marker = 0 THEN 'Нет'
                    ELSE 'Не указано'
                    END as "КПУ: Инвалид",
                    CASE 
                        WHEN old_apart.is_queue = 1 THEN 'Да'
                        WHEN old_apart.is_queue = 0 THEN 'Нет'
                        ELSE 'Не указано'
                    END as "КПУ: Очередник",
                    status.status AS "Статус"
                    from old_apart
                    JOIN status USING (status_id)
                    WHERE affair_id IN ({apart_ids})
                    ORDER BY affair_id'''),
                )
            return [row._mapping for row in result.fetchall()]

    async def get_current_table_with_last_offer(self, apart_ids : list[int]):
        async with self.db() as session: 
            apart_ids = ', '.join(list(map(str,apart_ids)))
            result = await session.execute(text(
                f'''
                with last_offer AS (
                    SELECT affair_id, KEY::bigint as new_apart_id FROM offer, jsonb_each(new_aparts)
                    where affair_id in ({apart_ids}) 
                    and offer_id in (select max(offer_id) from offer group by affair_id)
                )
                select 
                    old_apart.affair_id as "ID дела", 
                    old_apart.kpu_number as "Номер КПУ",
                    old_apart.fio as "ФИО",
                    old_apart.people_in_family as "Количество членов семьи",
                    old_apart.category as "Категория", 
                    old_apart.cad_num as "Кадастровый номер",
                    old_apart.district as "КПУ: Район",
                    old_apart.municipal_district as "КПУ: Муниципальный район",
                    old_apart.house_address as "КПУ: Адрес",
                    old_apart.apart_number as "КПУ: № квартиры",
                    old_apart.room_count as "КПУ: Количество комнат", 
                    old_apart."floor" as "КПУ: Этаж",
                    old_apart.total_living_area as "КПУ: Общая площадь",
                    old_apart.full_living_area as "КПУ: Полная жилая площадь",
                    old_apart.living_area as "КПУ: Жилая площадь", 
                    old_apart.is_queue as "Очередник",
                    CASE 
                        WHEN old_apart.is_special_needs_marker = 1 THEN 'Да'
                        WHEN old_apart.is_special_needs_marker = 0 THEN 'Нет'
                    ELSE 'Не указано'
                    END as "КПУ: Инвалид",
                    new_apart.new_apart_id as "ID НК", 
                    new_apart.district as "НК: Район", 
                    new_apart.municipal_district as "НК: Муниципальный район", 
                    new_apart.house_address as "НК: Адрес", 
                    new_apart.full_living_area as "НК: Полная жилая площадь",
                    new_apart.total_living_area as "НК: Общая площадь", 
                    new_apart.living_area as "НК: Жилая площадь",
                    CASE 
                        WHEN new_apart.for_special_needs_marker = 1 THEN 'Да'
                        WHEN new_apart.for_special_needs_marker = 0 THEN 'Нет'
                        ELSE 'Не указано'
                    END as "НК: Инвалидная",
                    old_status.status as "КПУ: статус",
                    new_status.status as "НК: статус"
                from old_apart 
                join last_offer using (affair_id)
                join new_apart using (new_apart_id)
                left join status as old_status on old_apart.status_id = old_status.status_id
                left join status as new_status on new_apart.status_id = new_status.status_id
                ORDER BY affair_id'''))
        
            return [row._mapping for row in result]
        
    async def set_district_notes(self, apart_ids: list[int], notes: str):
        async with self.db() as session:
            try:
                placeholder = ",".join(map(str, apart_ids))
                await session.execute(
                    text(f"""
                    UPDATE old_apart 
                    SET district_notes = :notes
                    WHERE affair_id IN ({placeholder})
                    """),
                    {"notes": notes},
                )
                await session.commit()
                return {"status": "done"}
            except Exception as error:
                session.rollback()
                raise error