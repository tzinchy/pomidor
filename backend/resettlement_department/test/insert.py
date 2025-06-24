import psycopg2
from datetime import date, timedelta
from config import get_connection
import json
from data.mock import old_apart_test_data, new_apart_test_data, offer_test_data

def insert_test_data(connection):
    with connection.cursor() as cursor:
        cursor.execute("""
            TRUNCATE TABLE 
                old_apart, new_apart, offer, order_decisions, 
                history, manual_load 
            RESTART IDENTITY CASCADE
        """)
        
    with connection.cursor() as cursor:

        insert_query = """
        INSERT INTO public.old_apart(
            affair_id, kpu_number, fio, people_in_family, cad_num, 
            house_address, apart_number, room_count, floor, living_area, 
            people_v_dele, people_uchet, apart_type, municipal_district, 
            is_special_needs_marker, is_queue, unom, total_living_area, full_living_area,
            status_id, created_at, updated_at
        )
        VALUES (
            %(affair_id)s, %(kpu_number)s, %(fio)s, %(people_in_family)s, %(cad_num)s,
            %(house_address)s, %(apart_number)s, %(room_count)s, %(floor)s, %(living_area)s,
            %(people_v_dele)s, %(people_uchet)s, %(apart_type)s, %(municipal_district)s,
            %(is_special_needs_marker)s, %(is_queue)s, %(unom)s, %(total_living_area)s, %(full_living_area)s,
            8, NOW(), NOW()
        )
        """

        for data in old_apart_test_data:
            cursor.execute(insert_query, data)
        
        for apart in new_apart_test_data:
            cursor.execute("""
                INSERT INTO new_apart (
                    new_apart_id, rsm_apart_id, cad_num, unom, un_kv,
                    house_address, apart_number, floor, room_count, living_area,
                    status_id, manual_load_id, history_id, created_at, updated_at
                ) VALUES (
                    %(new_apart_id)s, %(rsm_apart_id)s, %(cad_num)s, %(unom)s, %(un_kv)s,
                    %(house_address)s, %(apart_number)s, %(floor)s, %(room_count)s, %(living_area)s,
                    %(status_id)s, %(manual_load_id)s, %(history_id)s, NOW(), NOW()
                )
            """, apart)

        for offer in offer_test_data:
            cursor.execute("""
                INSERT INTO offer (
                    offer_id, affair_id, new_aparts
                ) VALUES (
                    %(offer_id)s, %(affair_id)s, %(new_aparts)s::jsonb
                )
            """, offer)

        connection.commit()

if __name__ == '__main__':
    conn = get_connection()
    try:
        insert_test_data(conn)
        print("Test data inserted successfully")
    finally:
        conn.close()