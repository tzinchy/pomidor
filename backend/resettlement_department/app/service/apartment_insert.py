import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime
from core.config import settings
from repository.database import project_managment_session
import re

def insert_data_to_old(df):
    connection = None  # Инициализация соединения
    cursor = None      # Инициализация курсора
    try:
        # Удаляем строки с пустыми ID
        old_apart = df.dropna(subset=["ID"])

        # Переименовываем колонки в соответствии с базой данных
        old_apart.rename(
            columns={
                "ID": "affair_id",
                "409858": "kpu_number",
                "409859": "fio",  # Исправлено: убрали дубликат
                "409860": "surname",
                "409861": "firstname",
                "409862": "lastname",
                "409863": "people_in_family",
                "409864": "category",
                "409865": "cad_num",
                "409866": "notes",
                "409867": "district",
                "409868": "municipal_district",
                "409869": "house_address",
                "409870": "apart_number",
                "409871": "room_count",
                "409872": "floor",
                "409873": "full_living_area",
                "409874": "living_area",
                "409875": "people_v_dele",
                "409876": "people_uchet",
                "409877": "total_living_area",
                "409878": "apart_type",
                "409879": "kpu_another",
                "410210": "type_of_settlement",
                "410229": 'rsm_status'
            },
            inplace=True,
        )
        print('replacing done')

        # Приведение типов данных
        old_apart["floor"] = old_apart["floor"].replace(np.nan, 0).astype("Int64")
        old_apart["category"] = old_apart["category"].replace(np.nan, 0).astype("Int64")
        old_apart["full_living_area"] = old_apart["full_living_area"].replace(np.nan, 0).astype(float)
        old_apart["total_living_area"] = old_apart["total_living_area"].replace(np.nan, 0).astype(float)
        old_apart["living_area"] = old_apart["living_area"].replace(np.nan, 0).astype(float)
        old_apart["people_v_dele"] = old_apart["people_v_dele"].replace(np.nan, 0).astype("Int64")
        old_apart["people_uchet"] = old_apart["people_uchet"].replace(np.nan, 0).astype("Int64")
        old_apart["people_in_family"] = old_apart["people_in_family"].replace(np.nan, 0).astype("Int64")
        print('astype done')

        # Добавляем колонку is_queue на основе регулярного выражения
        old_apart["is_queue"] = old_apart["kpu_another"].apply(
              lambda x: 1 if re.search(r"-01-", str(x)) else 0
        ).astype("Int64")
        print('ochered is done')

        # Выбираем нужные колонки
        old_apart = old_apart[
            [
                "affair_id",
                "kpu_number",
                "fio",
                "surname",
                "firstname",
                "lastname",
                "people_in_family",
                "cad_num",
                "notes",
                "district",
                "municipal_district",
                "house_address",
                "apart_number",
                "room_count",
                "floor",
                "full_living_area",
                "living_area",
                "people_v_dele",
                "people_uchet",
                "total_living_area",
                "apart_type",
                "category",
                "kpu_another",
                "is_queue",
                "type_of_settlement",
                "rsm_status"
            ]
        ]

        # Заменяем NaN на None для корректной вставки в базу данных
        old_apart = old_apart.replace({np.nan: None})
        print('replace none done')

        # Преобразуем DataFrame в список кортежей для массовой вставки
        args = list(old_apart.itertuples(index=False, name=None))

        # Подключаемся к базе данных PostgreSQL
        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )
        cursor = connection.cursor()

        # Формируем строку аргументов для SQL-запроса
        args_str = ",".join(
            "({})".format(
                ", ".join(
                    "'{}'".format(x.replace("'", "''"))
                    if isinstance(x, str)
                    else "NULL"
                    if x is None
                    else str(x)
                    for x in arg
                )
            )
            for arg in args
        )

        # Выполняем SQL-запрос для вставки данных
        cursor.execute(f"""
            INSERT INTO public.old_apart (
                affair_id, kpu_number, fio, surname, firstname, lastname, 
                people_in_family, cad_num, notes, district, municipal_district, house_address, 
                apart_number, room_count, floor, full_living_area, living_area, people_v_dele, 
                people_uchet, total_living_area, apart_type, category, kpu_another, is_queue, type_of_settlement, rsm_status
            )
            VALUES 
                {args_str}
            ON CONFLICT (affair_id) 
            DO UPDATE SET 
                kpu_number = EXCLUDED.kpu_number,
                fio = EXCLUDED.fio,
                surname = EXCLUDED.surname,
                firstname = EXCLUDED.firstname,
                lastname = EXCLUDED.lastname,
                people_in_family = EXCLUDED.people_in_family,
                cad_num = EXCLUDED.cad_num,
                notes = EXCLUDED.notes,
                district = EXCLUDED.district,
                municipal_district = EXCLUDED.municipal_district,
                house_address = EXCLUDED.house_address,
                apart_number = EXCLUDED.apart_number,
                room_count = EXCLUDED.room_count,
                floor = EXCLUDED.floor,
                full_living_area = EXCLUDED.full_living_area,
                living_area = EXCLUDED.living_area,
                people_v_dele = EXCLUDED.people_v_dele,
                people_uchet = EXCLUDED.people_uchet,
                total_living_area = EXCLUDED.total_living_area,
                apart_type = EXCLUDED.apart_type,
                category = EXCLUDED.category,
                kpu_another = EXCLUDED.kpu_another,
                is_queue = EXCLUDED.is_queue,
                type_of_settlement = EXCLUDED.type_of_settlement,
                rsm_status = EXCLUDED.rsm_status,
                updated_at = NOW()
        """)

        # Фиксируем изменения в основной транзакции
        connection.commit()

        # Обновляем статус успешного выполнения в отдельной транзакции
        cursor.execute(
            """UPDATE env.data_updates
                SET success = True,
                updated_at = NOW()
                WHERE name = 'old_aparts_kpu'
            """
        )
        connection.commit()
        return 1  # Успешное выполнение

    except Exception as e:
        print('ERROR', e)
        # Обновляем статус ошибки с отдельной обработкой
        status_updated = False
        try:
            if connection:
                connection.rollback()  # Сброс состояния транзакции
                # Создаем новый курсор для обновления статуса
                with connection.cursor() as status_cursor:
                    status_cursor.execute(
                        """UPDATE env.data_updates
                            SET success = False,
                            updated_at = NOW()
                            WHERE name = 'old_aparts_kpu'
                        """
                    )
                    connection.commit()
                    status_updated = True
        except Exception as status_error:
            print('ERROR updating status:', status_error)
        if not status_updated:
            # Попытка переподключиться, если соединение было потеряно
            try:
                new_conn = psycopg2.connect(
                    host=settings.project_management_setting.DB_HOST,
                    user=settings.project_management_setting.DB_USER,
                    password=settings.project_management_setting.DB_PASSWORD,
                    port=settings.project_management_setting.DB_PORT,
                    database=settings.project_management_setting.DB_NAME
                )
                with new_conn.cursor() as new_cursor:
                    new_cursor.execute(
                        """UPDATE env.data_updates
                            SET success = False,
                            updated_at = NOW()
                            WHERE name = 'old_aparts_kpu'
                        """
                    )
                    new_conn.commit()
                new_conn.close()
            except Exception as fallback_error:
                print('Fallback update failed:', fallback_error)
        return e

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


def new_apart_insert(new_apart_df: pd.DataFrame):
    connection = None
    cursor = None
    try:
        # Соответствие колонок DataFrame колонкам таблицы в БД
        column_mapping = {
            "ID": "new_apart_id",
            "375193": "rsm_id",
            "410610": "district",
            "410611": "municipal_district",
            "410612": "house_address",
            "410613": "apart_number",
            "410614": "floor",
            "410615": "room_count",
            "410616": "full_living_area",
            "410617": "total_living_area",
            "410618": "living_area",
            "410619": "building_id",
            "410620": "un_kv",
            "410621": "apart_type",
            "410622": "owner",
            "410623": "apart_kad_number",
            "410624": "room_kad_number",
            "411011": "for_special_needs_marker",
        }

        # Переименование колонок
        new_apart_df = new_apart_df.rename(columns=column_mapping)

        # Упорядочивание колонок
        expected_columns = [
            "new_apart_id", "building_id", "district", "municipal_district", "house_address", "apart_number",
            "floor", "full_living_area", "total_living_area", "living_area", "room_count", "rsm_id",
            "un_kv", "apart_type", "owner", "apart_kad_number", "room_kad_number", "for_special_needs_marker"
        ]
        new_apart_df = new_apart_df[expected_columns]

        # Преобразование типов
        new_apart_df["apart_number"] = new_apart_df["apart_number"].astype("Int64")
        special_needs_mapping = {"да": 1, "нет": 0}
        new_apart_df["for_special_needs_marker"] = (
            new_apart_df["for_special_needs_marker"].map(special_needs_mapping).fillna(0)
        )
        new_apart_df['full_living_area'] = new_apart_df['full_living_area'].fillna(0)
        new_apart_df['total_living_area'] = new_apart_df['total_living_area'].fillna(0)
        new_apart_df['living_area'] = new_apart_df['living_area'].fillna(0)
        # Заменяем NaN на None (для PostgreSQL)
        new_apart_df = new_apart_df.replace({np.nan: None})

        # Преобразуем в список кортежей для вставки
        args = list(new_apart_df.itertuples(index=False, name=None))

        print("Пример данных для вставки (первые 5 строк):")
        print(args[:5])
        print(f"Количество строк: {len(args)}")
        print(f"Количество колонок в DataFrame: {len(new_apart_df.columns)}")

        # Подключение к базе данных
        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )
        cursor = connection.cursor()

        # SQL-запрос с ON CONFLICT для обновления дублирующихся записей
        query = f"""
        INSERT INTO public.new_apart ({', '.join(expected_columns)})
        VALUES ({', '.join(['%s'] * len(expected_columns))})
        ON CONFLICT (new_apart_id) 
        DO UPDATE SET
            building_id = EXCLUDED.building_id,
            district = EXCLUDED.district,
            municipal_district = EXCLUDED.municipal_district,
            house_address = EXCLUDED.house_address,
            apart_number = EXCLUDED.apart_number,
            floor = EXCLUDED.floor,
            full_living_area = EXCLUDED.full_living_area,
            total_living_area = EXCLUDED.total_living_area,
            living_area = EXCLUDED.living_area,
            room_count = EXCLUDED.room_count,
            rsm_id = EXCLUDED.rsm_id,
            un_kv = EXCLUDED.un_kv,
            apart_type = EXCLUDED.apart_type,
            owner = EXCLUDED.owner,
            apart_kad_number = EXCLUDED.apart_kad_number,
            room_kad_number = EXCLUDED.room_kad_number,
            for_special_needs_marker = EXCLUDED.for_special_needs_marker,
            updated_at = NOW()
        """

        # Выполняем вставку с обновлением
        cursor.executemany(query, args)
        connection.commit()
        print("Вставка выполнена успешно!")

        # Обновление статуса в env.data_updates
        cursor.execute("""
            UPDATE env.data_updates
            SET success = TRUE, updated_at = NOW()
            WHERE name = 'new_aparts_resource'
        """)
        connection.commit()
        print("Статус обновлен.")

        return 1

    except Exception as e:
        print(f"Ошибка: {e}")
        if connection:
            connection.rollback()
            try:
                # Обновляем статус ошибки
                cursor.execute("""
                    UPDATE env.data_updates
                    SET success = FALSE, updated_at = NOW()
                    WHERE name = 'new_aparts_resource'
                """)
                connection.commit()
            except Exception as status_error:
                print(f"Не удалось обновить статус: {status_error}")
        return str(e)

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()


# Функция для преобразования строк в datetime с нужным форматом
def format_datetime_columns(df, columns):
    for col in columns:
        df.loc[:, col] = df[col].apply(
            lambda x: datetime.strptime(x, "%m/%d/%y %H:%M:%S").strftime(
                "%Y-%m-%d %H:%M:%S"
            )
            if pd.notnull(x)
            else None
        )
    return df

'''
# Функция для маппинга статуса в числовое поле status_id
def map_status(df):
    status_map = {
        "согласие": 1,
        "отказ": 2,
        "суд": 3,
        "фонд компенсация": 4,
        "фонд докупка": 5,
        "ожидание": 6,
        "подобрано": 7,
    }

    # Проверка значений перед маппингом
    unmapped_values = df.loc[~df["Result"].isin(status_map.keys()), "Result"].unique()
    if unmapped_values.size > 0:
        raise ValueError(f"Unmapped values in 'Result': {unmapped_values}")

    # Маппинг значений
    df["status_id"] = df["Result"].map(status_map)
    return df
'''
'''
def insert_offer(offer_df: pd.DataFrame):
    # Удаляем дубликаты по полю 'ID'
    offer_df = offer_df.drop_duplicates(subset=["ID"])

    # Преобразование формата даты и времени
    offer_df = format_datetime_columns(
        offer_df, ["SentenceDate", "GiveDate", "AnswerDate"]
    )

    # Применяем маппинг статуса
    offer_df = map_status(offer_df)

    # Заменяем NaN значения на None для корректной вставки в базу данных
    offer_df = offer_df.replace({np.nan: None})

    # Подготовка кортежей для вставки в SQL
    columns = [
        "ID",
        "SentenceDate",
        "GiveDate",
        "AnswerDate",
        "SentenceNumber",
        "SelectionAction",
        "Conditions",
        "Notes",
        "Claim",
        "SubjectID",
        "ObjectID",
        "status_id",
    ]
    args = list(offer_df[columns].itertuples(index=False, name=None))

    # Подключение к базе данных PostgreSQL
    connection  =  psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
    )
    cursor = connection.cursor()

    try:
        # Подготовка строки аргументов для SQL запроса
        args_str = ",".join(
            "({})".format(
                ", ".join(
                    "'{}'".format(x.replace("'", "''"))
                    if isinstance(x, str)
                    else "NULL"
                    if x is None
                    else str(x)
                    for x in arg
                )
            )
            for arg in args
        )

        # Выполнение SQL запроса для вставки данных
        cursor.execute(f"""
        INSERT INTO public.offer (
            offer_id, sentence_date, give_date, answer_date, 
            sentence_number, selection_action, conditions, notes, claim, 
            subject_id, object_id, status_id
        )
        VALUES
            {args_str}
        ON CONFLICT (offer_id) 
        DO UPDATE SET 
            sentence_date = EXCLUDED.sentence_date,
            give_date = EXCLUDED.give_date,
            answer_date = EXCLUDED.answer_date,
            sentence_number = EXCLUDED.sentence_number,
            selection_action = EXCLUDED.selection_action,
            conditions = EXCLUDED.conditions,
            notes = EXCLUDED.notes,
            claim = EXCLUDED.claim,
            subject_id = EXCLUDED.subject_id,
            object_id = EXCLUDED.object_id,
            status_id = EXCLUDED.status_id,
            updated_at = NOW()
        """)

        # Подтверждение изменений
        connection.commit()
        ds = 1

    except Exception as e:
        print("Error:", e)
        ds = 0

    # Закрытие курсора и соединения
    cursor.close()
    connection.close()

    return ds
'''
from psycopg2.extras import execute_values

def insert_to_db(new_apart_df, old_apart_df, cin_df):
    print('''======================================================
    1. Обработка и вставка для таблицы new_apart
    ======================================================
    Приведение столбца 'К_Инв/к' к нижнему регистру и замена значений на 1 или 0''')
    new_apart_df['К_Инв/к'] = new_apart_df['К_Инв/к'].astype(str).str.lower()
    new_apart_df['К_Инв/к'] = new_apart_df['К_Инв/к'].apply(lambda x: 1 if 'да' in x else 0)
    
    # Словарь для переименования колонок
    rename_new = {
        'Адрес_Округ': 'district', 
        'Адрес_Мун.округ': 'municipal_district',
        'Адрес_Короткий': 'house_address',
        'Адрес_№ кв': 'apart_number',
        'К_Комн': 'room_count',
        'К_Этаж': 'floor',
        'К_Ресурс': 'type_of_settlement',
        'Площадь общая': 'full_living_area',
        'Площадь общая(б/л)': 'total_living_area', 
        'Площадь жилая': 'living_area',
        'Сл.инф_APART_ID': 'up_id',
        'Кадастровый номер': 'cad_num',
        'К_Инв/к': 'for_special_needs_marker'
    }
    new_apart_df = new_apart_df[list(rename_new.keys())].rename(columns=rename_new)

    # Набор колонок для вставки в таблицу new_apart
    new_apart_required = [
        "district", "municipal_district", "house_address", "floor", "apart_number",
        "full_living_area", "total_living_area", "living_area", "room_count",
        "type_of_settlement", "for_special_needs_marker", "cad_num", "up_id"
    ]

    # Если каких-либо колонок нет, добавляем их со значением None
    for col in new_apart_required:
        if col not in new_apart_df.columns:
            new_apart_df[col] = None

    # Упорядочиваем DataFrame согласно требуемым колонкам
    new_apart_df = new_apart_df[new_apart_required]

    # Преобразуем DataFrame в список кортежей для вставки
    new_apart_values = [tuple(row) for row in new_apart_df.to_numpy()]

    new_apart_query = f"""
    INSERT INTO public.new_apart ({", ".join(new_apart_required)})
    VALUES %s
    ON CONFLICT (up_id)
    DO UPDATE SET updated_at = NOW();
    """
    print(new_apart_query)
    
    print('''======================================================
    2. Обработка и вставка для таблицы old_apart
    ======================================================''')
    rename_old = {
        'Округ' : 'district',
        'район' : 'municipal_district',
        'ФИО' : 'fio',
        'адрес дома' : 'house_address',
        '№ кв-ры' : 'apart_number',
        'Вид засел.' : 'type_of_settlement',
        'тип кв-ры' : 'apart_type',
        'кол-во комнат' : 'room_count',
        'площ. жил. пом.' : 'full_living_area',
        'общ. пл.' : 'total_living_area',
        'жил. пл.' : 'living_area',
        'Кол-во членов семьи' : 'people_v_dele',
        'Потребность' : 'is_special_needs_marker',
        'мин этаж': 'min_floor',
        'макс этаж' : 'max_floor',
        'Дата покупки' : 'buying_date',
        'ID' : 'affair_id'
    }
    old_apart_df = old_apart_df.rename(columns=rename_old)
    
    # Список всех колонок таблицы old_apart (исключая created_at и updated_at)
    old_apart_required = [
        "affair_id", "kpu_number", "fio", "surname", "firstname", "lastname",
        "people_in_family", "category", "cad_num", "notes", "documents", "district",
        "house_address", "apart_number", "room_count", "floor", "full_living_area",
        "living_area", "people_v_dele", "people_uchet", "total_living_area", "apart_type",
        "manipulation_notes", "municipal_district", "is_special_needs_marker", "min_floor",
        "max_floor", "buying_date", "type_of_settlement",
        "history_id", "rank", "kpu_another"
    ]
    
    # Добавляем отсутствующие колонки со значением None
    for col in old_apart_required:
        if col not in old_apart_df.columns:
            old_apart_df[col] = None
    
    # Упорядочиваем колонки
    old_apart_df = old_apart_df[old_apart_required]

    # Обработка даты
    if 'buying_date' in old_apart_df.columns:
        old_apart_df['buying_date'] = pd.to_datetime(old_apart_df['buying_date'], errors='coerce')
        old_apart_df['buying_date'] = old_apart_df['buying_date'].apply(lambda x: None if pd.isnull(x) else x)
    
    # Преобразование в кортежи
    old_apart_values = [tuple(row) for row in old_apart_df.to_numpy()]

    # Динамическое формирование SET для ON CONFLICT
    update_columns = [col for col in old_apart_required if col != 'affair_id']
    set_clause = ', '.join([f"{col} = EXCLUDED.{col}" for col in update_columns])
    
    old_apart_query = f"""
    INSERT INTO old_apart ({", ".join(old_apart_required)})
    VALUES %s
    ON CONFLICT (affair_id)
    DO UPDATE SET 
        updated_at = NOW(),
        {set_clause};
    """
    
    print('''======================================================
    Выполнение всех операций в рамках одного подключения
    ======================================================''')
    connection = psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME
    )

    # Обработка cin_df
    cin_df["УНОМ"] = cin_df["УНОМ"].astype(str)
    cin_df["Адрес отселения"] = cin_df["Адрес отселения"].astype(str)
    cin_df["Адрес ЦИНа"] = cin_df["Адрес ЦИНа"].astype(str)
    cin_df["График работы ЦИН"] = cin_df["График работы ЦИН"].astype(str)
    cin_df["График работы Департамента в ЦИНе"] = cin_df[
        "График работы Департамента в ЦИНе"
    ].astype(str)
    cin_df["Телефон для осмота"] = cin_df["Телефон для осмота"].astype(str)
    cin_df["Телефон для ответа"] = cin_df["Телефон для ответа"].astype(str)
    cin_df["Адрес Отдела"] = cin_df["Адрес Отдела"].astype(str)
    cin_df["Дата начала работы"] = pd.to_datetime(cin_df["Дата начала работы"], errors="coerce").dt.date

    data_to_insert = []
    for _, row in cin_df.iterrows():
        data_to_insert.append(
            {
                "unom": row["УНОМ"],
                "old_address": row["Адрес отселения"],
                "cin_address": row["Адрес ЦИНа"],
                "cin_schedule": row["График работы ЦИН"],
                "dep_schedule": row["График работы Департамента в ЦИНе"],
                "phone_osmotr": row["Телефон для осмота"] if pd.notna(row["Телефон для осмота"]) else None,
                "phone_otvet": row["Телефон для ответа"] if pd.notna(row["Телефон для ответа"]) else None,
                "start_date": row["Дата начала работы"] if pd.notna(row["Дата начала работы"]) else None,
                "otdel": row["Адрес Отдела"],
            }
        )

    cursor = connection.cursor()
    print(cin_df)

    try:
        # Вставка в new_apart
        execute_values(cursor, new_apart_query, new_apart_values)
        # Вставка в old_apart
        execute_values(cursor, old_apart_query, old_apart_values)
        # Вставка в cin
        for data in data_to_insert:
            cursor.execute(
                """
                INSERT INTO public.cin (
                    unom, old_address, cin_address, cin_schedule, dep_schedule, phone_osmotr, phone_otvet, start_date, otdel
                ) VALUES (
                    %(unom)s, %(old_address)s, %(cin_address)s, %(cin_schedule)s, %(dep_schedule)s, %(phone_osmotr)s, %(phone_otvet)s, %(start_date)s,  %(otdel)s
                )
                ON CONFLICT (unom) DO UPDATE SET 
                    old_address = EXCLUDED.old_address, 
                    cin_address = EXCLUDED.cin_address, 
                    cin_schedule = EXCLUDED.cin_schedule, 
                    dep_schedule = EXCLUDED.dep_schedule, 
                    phone_osmotr = EXCLUDED.phone_osmotr, 
                    phone_otvet = EXCLUDED.phone_otvet, 
                    start_date = EXCLUDED.start_date, 
                    otdel = EXCLUDED.otdel 
            """,
                data,
            )
        connection.commit()
    except Exception as e:
        connection.rollback()
        raise e
    finally:
        cursor.close()
        connection.close()