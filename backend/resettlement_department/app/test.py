import psycopg2
import pandas as pd
from core.config import settings
from datetime import datetime
import json

def get_db_connection():
    return psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME
    )

def rematch(apart_ids):
    for apart_id in apart_ids:
        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()

                # Запрос для получения данных старой квартиры
                apart_query = '''
                    SELECT affair_id, room_count, full_living_area, total_living_area, living_area, 
                    is_special_needs_marker, is_queue, queue_square, new_house_addresses, rank, 
                    (SELECT MAX(rank) FROM public.new_apart WHERE new_apart_id::text IN 
                    (SELECT key FROM public.offer, LATERAL json_each_text(new_aparts::json) AS j(key, value) WHERE affair_id = %s)) AS new_apart_rank
                    FROM public.old_apart
                    JOIN history USING(history_id)
                    WHERE affair_id = %s
                '''
                cursor.execute(apart_query, (apart_id, apart_id))
                aparts = cursor.fetchall()

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
                        apart[0]   # affair_id
                    )

                    # Поиск подходящей новой квартиры
                    new_apart_query = '''
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
                    '''
                    cursor.execute(new_apart_query, new_apart_params)
                    new_aparts = cursor.fetchall()

                    if new_aparts:
                        # Обновление данных о новой квартире
                        update_query = """
                            UPDATE public.offer
                            SET new_aparts = (
                                SELECT jsonb_object_agg(key, jsonb_set(value, '{status_id}', '2', false))
                                FROM jsonb_each(new_aparts)
                            ) || jsonb_build_object(%s, jsonb_build_object('status_id', 7))
                            WHERE affair_id = %s;
                        """
                        cursor.execute(update_query, (new_aparts[0][0], apart[0]))
                        conn.commit()  # Фиксация изменений
                        print(f"Обновлено для apart_id {apart_id}: {new_aparts[0][0]}")
                    else:
                        print(f"Новая квартира не найдена для apart_id {apart_id}")
                else:
                    print(f'Старая квартира не найдена для apart_id {apart_id}')

        except Exception as e:
            print(f"Ошибка при обработке apart_id {apart_id}: {e}")
            conn.rollback()  # Откат в случае ошибки

    return None

rematch([100107, 100108, 100110, 1001070, 1001080, 1001100])