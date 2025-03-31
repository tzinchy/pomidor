import psycopg2
from core.config import settings
from repository.database import project_managment_session
from handlers.httpexceptions import  HTTPException
from fastapi import status



def get_db_connection():
    return psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME,
    )


async def rematch(apart_ids):
    print(apart_ids)
    cant_offer_aparts_raise_ids = {}
    for apart_id in apart_ids:
        try:
            async with project_managment_session() as session:
                apart_query = """
                with unnst_max_rank AS (
                select affair_id, (key)::bigint as new_apart_id, value->>'status_id' as status_id from public.offer, jsonb_each(new_aparts)
                where (value->>'status_id')::integer != 1  
                ),
                unnst_join AS (
                SELECT 
                affair_id,
                new_apart_id,
                room_count, 
                max(rank) as max_rank
                FROM unnst_max_rank
                join new_apart using (new_apart_id)
                group by affair_id, new_apart_id, room_count,status_id
                ),
				build_max_rank_json AS (
                SELECT affair_id, jsonb_object_agg(room_count::integer, max_rank) max_rank_by_room_count from unnst_join
				where affair_id = 902915
                group by affair_id)
				SELECT 
				build_max_rank_json.affair_id,
                room_count, 
                full_living_area,
                total_living_area,
                living_area, 
                is_special_needs_marker, 
                is_queue,
                queue_square,
                new_house_addresses, 
                rank, 
				max_rank_by_room_count
				FROM build_max_rank_json 
				JOIN old_apart USING (affair_id)
				JOIN history USING (history_id)
                """
                apart_info = session.execute(apart_query)
        """
                if aparts:
                    apart = aparts[0]
                    # Подготовка параметров для поиска новой квартиры
                    new_apart_params = (
                        apart[1],  # room_count
                        apart[2],  # full_living_area
                        apart[3],  # total_living_area
                        apart[4],  # living_area
                        apart[5],  # is_special_needs_marker
                        tuple(apart[8]),  # new_house_addresses
                        apart[9],  # rank
                        apart[10],  # new_apart_rank
                        apart[0],  # affair_id
                    )

                    # Поиск подходящей новой квартиры
                    new_apart_query = """
                        SELECT new_apart_id, room_count, full_living_area, total_living_area, living_area, rank 
                        FROM public.new_apart
                        WHERE new_apart_id::text NOT IN 
                            (SELECT key FROM public.offer, 
                            LATERAL json_each_text(new_aparts::json) AS j(key, value) 
                            WHERE (value::json->>'status_id')::int != 2)
                        AND room_count = %s 
                        AND full_living_area >= %s 
                        AND total_living_area >= %s 
                        AND living_area >= %s 
                        AND for_special_needs_marker = %s 
                        AND house_address IN %s 
                        AND rank IN (%s, %s)
                        AND new_apart_id::text NOT IN 
                            (SELECT key FROM public.offer, LATERAL json_each_text(new_aparts::json) AS j(key, value) 
                            WHERE affair_id = %s)
                        ORDER BY rank, (full_living_area + living_area) 
                        LIMIT 1
                    """
                    cursor.execute(new_apart_query, new_apart_params)
                    new_aparts = cursor.fetchall()

                    if new_aparts:
                        new_apart_id = new_aparts[0][0]  # ID новой квартиры

                        # Шаг 1: Обновление последней записи
                        update_query = """
                            UPDATE public.offer
                            SET
                            status_id = 2, 
                            new_aparts = (
                                SELECT jsonb_object_agg(key, jsonb_set(value, '{status_id}', '2', false))
                                FROM jsonb_each(new_aparts)
                            ) 
                            WHERE affair_id = %s
                            AND created_at = (SELECT MAX(created_at) FROM public.offer WHERE affair_id = %s);
                        """
                        cursor.execute(update_query, (apart[0], apart[0]))
                        print(
                            f"Обновлена последняя запись для apart_id {apart_id}: {new_apart_id}"
                        )

                        # Шаг 2: Вставка новой записи
                        insert_query = """
                            INSERT INTO public.offer (affair_id, new_aparts, status_id)
                            VALUES (%s, jsonb_build_object(%s, jsonb_build_object('status_id', 7)), 7);
                        """
                        cursor.execute(insert_query, (apart[0], new_apart_id))
                        print(
                            f"Вставлена новая запись для apart_id {apart_id}: {new_apart_id}"
                        )

                        conn.commit()  # Фиксация изменений
                    else:
                        raise HTTPException(
                            status_code=status.HTTP_409_CONFLICT,
                            detail="Не нашлось подходящей квартиры!",
                        )

                else:
                    raise HTTPException(
                        status_code=status.HTTP_409_CONFLICT,
                        detail="Не нашлось подходящей старой квартиры!",
                    )

        except Exception as e:
            print(f"Ошибка при обработке apart_id {apart_id}: {e}")
            conn.rollback()
            raise e

    return None
