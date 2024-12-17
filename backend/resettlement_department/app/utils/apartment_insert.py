import pandas as pd
import numpy as np
import psycopg2
from datetime import datetime
from sqlalchemy import text
from dotenv import load_dotenv
from core.config import Settings  # Импорт класса Settings для конфигурации

# Подключение к базе данных с использованием Settings
def get_db_connection():
    return psycopg2.connect(
        host=Settings.DB_HOST,
        port=Settings.DB_PORT,
        database=Settings.DB_NAME,
        user=Settings.DB_USER,
        password=Settings.DB_PASS
    )

# Функция для вставки данных в family_apartment_needs
def insert_data_to_needs(family_apartments_needs_df):
    family_apartments_needs_df = family_apartments_needs_df.dropna(subset=['affair_id'])
    family_apartments_needs_df.rename(columns={'CountBusiness_x': 'kpu_num', 'ID': 'up_id'}, inplace=True)
    family_apartments_needs_df = family_apartments_needs_df[['kpu_num', 'up_id', 'affair_id']].replace({np.nan: None})
    args = list(family_apartments_needs_df.itertuples(index=False, name=None))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        args_str = ",".join(
            "({})".format(", ".join(
                "'{}'".format(x.replace("'", "''")) if isinstance(x, str) else "NULL" if x is None else str(x)
                for x in arg))
            for arg in args
        )
        cursor.execute(f"""
            INSERT INTO public.family_apartment_needs (kpu_num, up_id, affair_id)
            VALUES {args_str}
            ON CONFLICT (up_id) 
            DO UPDATE SET 
                kpu_num = EXCLUDED.kpu_num,
                affair_id = EXCLUDED.affair_id,
                updated_at = NOW()
        """)
        connection.commit()
        return {"status": "success", "rows": len(args)}
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        connection.close()


# Функция для вставки данных в family_structure
def insert_data_to_structure(family_structure_df):
    family_structure_df = family_structure_df.dropna(subset=['ID'])
    family_structure_df.rename(columns={
        'ID': 'affair_id',
        'КПУ_Дело_№ полный(новый)': 'kpu_number',
        'КПУ_Заявитель_Фамилия': 'surname',
        'КПУ_Заявитель_Имя': 'firstname',
        'КПУ_Заявитель_Отчество': 'lastname',
        'К_Тип_Кв': 'apart_type',
        'К_Комн': 'room_count',
        'К_Этаж': 'floor',
        'К_Общ': 'full_living_area'
    }, inplace=True)
    family_structure_df = family_structure_df.replace({np.nan: None})
    args = list(family_structure_df.itertuples(index=False, name=None))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        args_str = ",".join(
            "({})".format(", ".join(
                "'{}'".format(x.replace("'", "''")) if isinstance(x, str) else "NULL" if x is None else str(x)
                for x in arg))
            for arg in args
        )
        cursor.execute(f"""
            INSERT INTO public.family_structure (
                affair_id, kpu_number, surname, firstname, lastname, apart_type, room_count, floor, full_living_area
            )
            VALUES {args_str}
            ON CONFLICT (affair_id) 
            DO UPDATE SET 
                kpu_number = EXCLUDED.kpu_number,
                surname = EXCLUDED.surname,
                firstname = EXCLUDED.firstname,
                lastname = EXCLUDED.lastname,
                apart_type = EXCLUDED.apart_type,
                room_count = EXCLUDED.room_count,
                floor = EXCLUDED.floor,
                full_living_area = EXCLUDED.full_living_area,
                updated_at = NOW()
        """)
        connection.commit()
        return {"status": "success", "rows": len(args)}
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        connection.close()


# Функция для вставки данных в new_apart
def new_apart_insert(new_apart_df):
    column_mapping = {
        'Сл.инф_APART_ID': 'new_apart_id',
        'Сл.инф_UNOM': 'building_id',
        'Адрес_Округ': 'district',
        'Адрес_Короткий': 'house_address',
        'Адрес_№ кв': 'apart_number'
    }
    new_apart_df = new_apart_df.rename(columns=column_mapping).replace({np.nan: None})
    args = list(new_apart_df.itertuples(index=False, name=None))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        args_str = ",".join(
            "({})".format(", ".join(
                "'{}'".format(x.replace("'", "''")) if isinstance(x, str) else "NULL" if x is None else str(x)
                for x in arg))
            for arg in args
        )
        cursor.execute(f"""
            INSERT INTO public.new_apart (
                new_apart_id, building_id, district, house_address, apart_number
            )
            VALUES {args_str}
            ON CONFLICT (new_apart_id)
            DO UPDATE SET
                building_id = EXCLUDED.building_id,
                district = EXCLUDED.district,
                house_address = EXCLUDED.house_address,
                apart_number = EXCLUDED.apart_number,
                updated_at = NOW()
        """)
        connection.commit()
        return {"status": "success", "rows": len(args)}
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        connection.close()


# Функция для вставки данных в offer
def insert_offer(offer_df):
    offer_df = offer_df.drop_duplicates(subset=['ID'])
    offer_df = offer_df.replace({np.nan: None})
    args = list(offer_df.itertuples(index=False, name=None))

    connection = get_db_connection()
    cursor = connection.cursor()
    try:
        args_str = ",".join(
            "({})".format(", ".join(
                "'{}'".format(x.replace("'", "''")) if isinstance(x, str) else "NULL" if x is None else str(x)
                for x in arg))
            for arg in args
        )
        cursor.execute(f"""
            INSERT INTO public.offer (
                offer_id, sentence_date, givedate, registry, answer_date
            )
            VALUES {args_str}
            ON CONFLICT (offer_id)
            DO UPDATE SET
                sentence_date = EXCLUDED.sentence_date,
                givedate = EXCLUDED.givedate,
                registry = EXCLUDED.registry,
                answer_date = EXCLUDED.answer_date,
                updated_at = NOW()
        """)
        connection.commit()
        return {"status": "success", "rows": len(args)}
    except Exception as e:
        connection.rollback()
        return {"status": "error", "message": str(e)}
    finally:
        cursor.close()
        connection.close()
