from sqlalchemy import text
from schema.apartment import ApartTypeSchema
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
                return [dict(row._mapping) for row in result]
            except Exception as error:
                logger.error(f"Error executing query: {error}")
                raise

    async def get_apartment_by_id(self, apart_id: int, apart_type: str) -> dict:
        """
        Получить всю информацию о квартире по ID.
        """
        if apart_type not in ApartTypeSchema:
            raise ValueError(f"Invalid apartment type: {apart_type}")

        query_params = {"apart_id": apart_id}

        if apart_type == "NewApartment":
<<<<<<< HEAD
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/NewApartById.sql")
        elif apart_type == "OldApart":
            query = read_sql_query(f"{RECOMMENDATION_FILE_PATH}/OldApartById.sql")
=======
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
>>>>>>> main
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
                    await session.execute(update_query, {"status" : "Отказ", "apart_id": old_apart_id})
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
                if apart_type == ApartTypeSchema.OLD:
                    result = await session.execute(
                        text("DELETE FROM offer WHERE affair_id = :apart_id AND offer_id = (select max(offer_id) from offer where affair_id = :apart_id)"),
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

    async def update_status_for_apart(self, apart_id, status, apart_type):
        async with self.db() as session:
            try:
                if apart_type == ApartTypeSchema.OLD:

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
    
    async def set_private_for_new_aparts(self, new_apart_ids, status: bool = True):
        async with self.db() as session:
            try:
                # Проверяем, что new_apart_ids не пустой
                if not new_apart_ids:
                    raise ValueError("The list of apartment IDs is empty.")
                
                # Формируем строку с плейсхолдерами для каждого ID
                placeholders = ', '.join([':id_' + str(i) for i in range(len(new_apart_ids))])
                
                # Формируем словарь с параметрами
                params = {'status': status}
                params.update({f'id_{i}': id for i, id in enumerate(new_apart_ids)})
                
                # Используем параметризованный запрос для безопасности
                query = text(f'UPDATE new_apart SET is_private = :status WHERE new_apart_id IN ({placeholders})')
                
                # Передаем параметры в правильном формате
                await session.execute(query, params)
                await session.commit()
            except Exception as error:
                print(error)
                raise SomethingWrong("Something went wrong while updating the apartments.")
            
    async def set_cancell_reason(self, apartment_id, min_floor, max_floor, unom, entrance, apartment_layout, notes):
        async with self.db() as session:
            try:
                # Вставляем данные в таблицу decline_reason
                insert_query = text('''
                    INSERT INTO public.decline_reason 
                    (min_floor, max_floor, unom, entrance, apartment_layout, notes)
                    VALUES (:min_floor, :max_floor, :unom, :entrance, :apartment_layout, :notes)
                    RETURNING declined_reason_id;
                ''')
                result = await session.execute(insert_query, {
                    'min_floor': min_floor,
                    'max_floor': max_floor,
                    'unom': unom,
                    'entrance': entrance,
                    'apartment_layout': apartment_layout,
                    'notes': notes
                })
                declined_reason_id = result.scalar()

                # Обновляем статус в таблице offer
                update_query = text('''
                    WITH changeStatus AS (
                        SELECT status_id 
                        FROM status 
                        WHERE status = :status
                    ),
                    latest_offer AS (
                        SELECT offer_id 
                        FROM public.offer 
                        WHERE affair_id = :apart_id
                        ORDER BY created_at DESC 
                        LIMIT 1
                    )
                    UPDATE public.offer
                    SET 
                        status_id = (SELECT status_id FROM changeStatus),
                        declined_reason_id = :declined_reason_id, 
                    new_aparts = (
                        SELECT jsonb_object_agg(key, jsonb_set(value, '{status_id}', to_jsonb((SELECT status_id FROM changeStatus)), false))
                        FROM jsonb_each(new_aparts)
                    ) 
                    WHERE offer_id = (SELECT offer_id FROM latest_offer);
                ''')
                await session.execute(update_query, {
                    'status': 'Отказ',  
                    'apart_id': apartment_id,
                    'declined_reason_id' : declined_reason_id  
                })

                await session.commit()
                return declined_reason_id
            except Exception as error:
                print(error)
                await session.rollback()
                raise SomethingWrong