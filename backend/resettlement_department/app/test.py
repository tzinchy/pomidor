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

def rematch(apart_id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()

            apart_query = '''
                SELECT affair_id, room_count, full_living_area, total_living_area, living_area, 
                is_special_needs_marker, is_queue, queue_square, history_id, rank
                FROM public.old_apart
                where affair_id = %s
            '''
            cursor.execute(apart_query, tuple(apart_id, ))
            apart = cursor.fetchall()[0]
            new_apart_params = (apart[1], apart[2], apart[3], apart[4], apart[5], apart[8])
            print(new_apart_params, apart[-1])

            
            new_apart_query = '''
                SELECT new_apart_id, room_count, full_living_area, total_living_area, living_area, rank FROM public.new_apart
                where new_apart_id::text not in 
                (SELECT key FROM public.offer, 
                LATERAL json_each_text(new_aparts::json) AS j(key, value) 
                WHERE (value::json->>'status_id')::int != 2)
                and room_count = %s and full_living_area >= %s and total_living_area >= %s and living_area >= %s and for_special_needs_marker = %s and history_id = %s 
                order by (new_apart.full_living_area + new_apart.living_area)
            '''
            cursor.execute(new_apart_query, new_apart_params)
            new_aparts = cursor.fetchall()
            df_new_aparts = pd.DataFrame(new_aparts,columns=[
                        "new_apart_id", "room_count", "full_living_area", "total_living_area", "living_area", "rank"
                    ],
                )
            
            print(df_new_aparts)

    except Exception as e:
        print(f"Error: {e}")
        raise     

    return None

rematch((894138,))