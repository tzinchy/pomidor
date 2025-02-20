import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime
from core.config import settings
from repository.database import project_managment_session
'''
def insert_data_to_needs(family_apartments_needs_df):
    """dataframe income data!"""
    connection = None
    cursor = None
    try:
        # 1. Drop rows where 'affair_id' is NaN
        family_apartments_needs_df = family_apartments_needs_df.dropna(
            subset=["affair_id"]
        )

        # Rename columns to match database fields
        family_apartments_needs_df.rename(
            columns={"CountBusiness_x": "kpu_num", "ID": "up_id"}, inplace=True
        )
        family_apartments_needs_df = family_apartments_needs_df[
            ["kpu_num", "up_id", "affair_id"]
        ]

        # Replace NaN with None
        family_apartments_needs_df = family_apartments_needs_df.replace({np.nan: None})

        # Convert DataFrame rows into a list of tuples for bulk insert
        args = list(family_apartments_needs_df.itertuples(index=False, name=None))

        # Connect to the PostgreSQL database
        connection  =  psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )
        cursor = connection.cursor()

        # Prepare the arguments string for the SQL query
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

        # Execute the SQL query
        cursor.execute(f"""
        INSERT INTO public.family_apartment_needs (kpu_num, up_id, affair_id)
        VALUES
        {args_str}
        ON CONFLICT (up_id) 
        DO UPDATE SET 
            kpu_num = EXCLUDED.kpu_num,
            affair_id = EXCLUDED.affair_id,
            updated_at = NOW()
        """)

        connection.commit()
        ds = 1

    except Exception as e:
        ds = e

    finally:
        if cursor:
            cursor.close()
        if connection:
            connection.close()
        return ds


def insert_data_to_structure(family_structure):
    """dataframe income data!"""
    try:
        family_structure = family_structure.dropna(subset=["ID"])

        # 2. Rename columns to match the database schema
        family_structure.rename(
            columns={
                "ID": "affair_id",
                "КПУ_Дело_№ полный(новый)": "kpu_number",
                "КПУ_Заявитель_Фамилия": "surname",
                "КПУ_Заявитель_Имя": "firstname",
                "КПУ_Заявитель_Отчество": "lastname",
                "КПУ_кадастровый_номер_адреса": "cad_num",
                "К_Тип_Кв": "apart_type",
                "К_Комн": "room_count",
                "К_Этаж": "floor",
                "К_Общ": "full_living_area",
                "К_Общ(б/л)": "total_living_area",
                "К_Жил": "living_area",
                "КПУ_ФИО": "fio",
                "Notes": "notes",
                "Адрес_Округ": "district",
                "Адрес_Короткий": "house_address",
                "Адрес_№ кв": "apart_number",
                "КПУ_Чел.в деле": "people_v_dele",
                "КПУ_Чел.учете": "people_uchet",
                "КПУ_Чел.в семье": "people_in_family",
                "КПУ_Состояние": "status_id",
                "КПУ_Направление": "category",
            },
            inplace=True,
        )

        status_mapping = {
            "в орд.гр": 1,
            "в плане": 2,
            "на учете": 3,
            "перед.в др.АО": 4,
            "пред.пл.": 5,
            "снято": 6,
        }
        # Применение маппинга
        family_structure["status_id"] = family_structure["status_id"].apply(
            lambda x: status_mapping.get(x, x)
        )
        family_structure["floor"] = family_structure["floor"].astype("Int64")
        family_structure["category"] = family_structure["category"].astype("Int64")
        family_structure["full_living_area"] = family_structure[
            "full_living_area"
        ].astype(float)
        family_structure["total_living_area"] = family_structure[
            "total_living_area"
        ].astype(float)
        family_structure["living_area"] = family_structure["living_area"].astype(float)
        family_structure["people_v_dele"] = family_structure["people_v_dele"].astype(
            "Int64"
        )
        family_structure["people_uchet"] = family_structure["people_uchet"].astype(
            "Int64"
        )
        family_structure["people_in_family"] = family_structure[
            "people_in_family"
        ].astype("Int64")
        family_structure = family_structure[
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
                "status_id",
                "category",
            ]
        ]
        # Convert to list of dictionaries for batch insertion
        family_structure = family_structure.replace({np.nan: None})
        family_structure["status_id"] = family_structure["status_id"].astype("Int64")
        # Convert DataFrame rows into a list of tuples for bulk insert
        args = list(family_structure.itertuples(index=False, name=None))
        # Prepare the arguments string for the SQL query

        # Connect to the PostgreSQL database
        connection  =  psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )
        cursor = connection.cursor()

        # Prepare the arguments string for the SQL query
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

        cursor.execute(f"""
        INSERT INTO public.family_structure (
            affair_id, kpu_number, fio, surname, firstname, lastname, 
            people_in_family, cad_num, notes, district, house_address, 
            apart_number, room_count, floor, full_living_area, living_area, people_v_dele, 
            people_uchet, total_living_area, apart_type, status_id, category
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
        status_id = EXCLUDED.status_id,
        category = EXCLUDED.category,
        updated_at = NOW()
    """)
        connection.commit()
        ds = 1
    except Exception as e:
        ds = e
    finally:
        cursor.close()
        connection.close()
        return ds


def new_apart_insert(new_apart_df: pd.DataFrame):
    try:
        # Define the column renaming mapping
        column_mapping = {
            "Сл.инф_APART_ID": "new_apart_id",
            "Сл.инф_UNOM": "building_id",
            "Адрес_Округ": "district",
            "Адрес_Мун.округ": "municipal_district",
            "Адрес_Короткий": "house_address",
            "Адрес_№ кв": "apart_number",
            "К_Этаж": "floor",
            "Площадь общая": "full_living_area",
            "Площадь общая(б/л)": "total_living_area",
            "Площадь жилая": "living_area",
            "К_Комн": "room_count",
            "К_Тип.пл": "type_of_settlement",
            "К_Ресурс": "apart_resource",
            "Сл.инф_UNKV": "un_kv",
            "Распорядитель_Название": "owner",
            "К_Состояние": "status",
            "К_Инв/к": "for_special_needs_marker",
            "РСМ_Кад номер, квартира": "apart_kad_number",
            "РСМ, Кад номер, комната": "room_kad_number",
            "Адрес_улица": "street_address",
            "Адрес_дом_№": "house_number",
            "Адрес_дом_индекс": "house_index",
            "Адрес_корпус_№": "bulding_body_number",
            "id_up": "up_id",
            "notes": "notes",
        }

        # Rename columns in the DataFrame
        new_apart_df = new_apart_df.rename(columns=column_mapping)
        print("Column mapping applied successfully.")

        # Apply mapping for 'for_special_needs_marker'
        special_needs_mapping = {"да": 1, "нет": 0}
        new_apart_df["for_special_needs_marker"] = (
            new_apart_df["for_special_needs_marker"]
            .map(special_needs_mapping)
            .fillna(0)
        )

        # Replace NaN values with None for SQL compatibility
        new_apart_df = new_apart_df.replace({np.nan: None})

        # Check for duplicates in 'new_apart_id' and print them if any
        duplicates = new_apart_df[new_apart_df.duplicated(subset=["up_id"], keep=False)]
        if not duplicates.empty:
            print("Duplicate rows found for 'new_apart_id':")
            print(duplicates)
            new_apart_df = new_apart_df.drop_duplicates(subset=["up_id"])
        else:
            print("No duplicates found for 'new_apart_id'.")

        # Convert DataFrame rows into a list of tuples for bulk insert
        args = list(new_apart_df.itertuples(index=False, name=None))
        print("Data converted to list of tuples for insertion.")

        connection  =  psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )
        cursor = connection.cursor()

        # Prepare the arguments string for the SQL query
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

        # Define the columns to insert or update
        insert_columns = (
            "new_apart_id, building_id, district, municipal_district, house_address, apart_number, "
            "floor, full_living_area, total_living_area, living_area, room_count, type_of_settlement, "
            "apart_resource, un_kv, owner, status, for_special_needs_marker, apart_kad_number, "
            "room_kad_number, street_address, house_number, house_index, bulding_body_number, up_id, notes"
        )

        # Execute the insert query with conflict handling
        cursor.execute(f"""
        INSERT INTO public.new_apart ({insert_columns})
            VALUES {args_str}
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
                type_of_settlement = EXCLUDED.type_of_settlement,
                apart_resource = EXCLUDED.apart_resource,
                un_kv = EXCLUDED.un_kv,
                owner = EXCLUDED.owner,
                status = EXCLUDED.status,
                for_special_needs_marker = EXCLUDED.for_special_needs_marker,
                apart_kad_number = EXCLUDED.apart_kad_number,
                room_kad_number = EXCLUDED.room_kad_number,
                street_address = EXCLUDED.street_address,
                house_number = EXCLUDED.house_number,
                house_index = EXCLUDED.house_index,
                bulding_body_number = EXCLUDED.bulding_body_number,
                up_id = EXCLUDED.up_id,
                notes = EXCLUDED.notes,
                updated_at = NOW()
        """)

        # Commit the transaction
        connection.commit()
        print("Insertion successful.")
        ds = 1
    except Exception as e:
        print(
            "An error occurred:", e
        )  # Capture the exception for logging or troubleshooting
        ds = e
    finally:
        # Close cursor and connection
        cursor.close()
        connection.close()
        return ds


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
        "type_of_settlement", "for_special_needs_marker", "cad_num", "house_number", "up_id"
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
    2. Обработка и вставка для таблицы family_structure
    ======================================================
    Словарь для переименования колонок старых данных (семейная структура)''')
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
    
    # Обработка столбца даты: преобразуем в datetime, а затем заменяем NaT на None
    if 'buying_date' in old_apart_df.columns:
        old_apart_df['buying_date'] = pd.to_datetime(old_apart_df['buying_date'], errors='coerce')
        old_apart_df['buying_date'] = old_apart_df['buying_date'].apply(lambda x: None if pd.isnull(x) else x)
    
    # Если для остальных столбцов не нужно заменять NaN, то не применяем fillna ко всему DataFrame!
    # old_apart_df = old_apart_df.fillna(0)  # этот шаг закомментирован, чтобы не заменять даты

    family_structure_required = [
        'district', 'municipal_district', 'fio', 'house_address', 'apart_number',
        'type_of_settlement', 'apart_type', 'room_count', 'full_living_area',
        'total_living_area', 'living_area', 'people_v_dele', 'is_special_needs_marker',
        'min_floor', 'max_floor', 'buying_date', 'affair_id'
    ]
    for col in family_structure_required:
        if col not in old_apart_df.columns:
            old_apart_df[col] = None
    old_apart_df = old_apart_df[family_structure_required]

    family_structure_values = [tuple(row) for row in old_apart_df.to_numpy()]

    family_structure_query = f"""
    INSERT INTO family_structure ({", ".join(family_structure_required)})
    VALUES %s
    ON CONFLICT (affair_id)
    DO UPDATE SET updated_at = NOW();
    """

    print('''======================================================
    3. Обработка и вставка для таблицы family_apartmnet_needs
    ======================================================
    Предполагаем, что в этой таблице требуется только affair_id.
    Из DataFrame с семейной структурой получаем список идентификаторов.''')
    family_apartment_needs_values = [(row,) for row in old_apart_df['affair_id'].tolist()]

    family_apartment_needs_query = """
    INSERT INTO family_apartment_needs (affair_id)
    VALUES %s
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

    # Преобразование типов данных
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
                "phone_osmotr": row["Телефон для осмота"]
                if pd.notna(row["Телефон для осмота"])
                else None,
                "phone_otvet": row["Телефон для ответа"]
                if pd.notna(row["Телефон для ответа"])
                else None,
                "start_date": row["Дата начала работы"]
                if pd.notna(row["Дата начала работы"])
                else None,
                "otdel": row["Адрес Отдела"],
            }
        )

    cursor = connection.cursor()
    print(cin_df)

    try:
        # Вставка в new_apart
        print(new_apart_values)
        execute_values(cursor, new_apart_query, new_apart_values)
        print(1)
        # Вставка в family_structure
        execute_values(cursor, family_structure_query, family_structure_values)
        print(2)
        #Вставка в family_apartmnet_needs
        execute_values(cursor, family_apartment_needs_query, family_apartment_needs_values)
        print(3)
        for data in data_to_insert:
            cursor.execute(
                """
                INSERT INTO public.cin (
                    unom, old_address, cin_address, cin_schedule, dep_schedule, phone_osmotr, phone_otvet, start_date, otdel
                ) VALUES (
                    %(unom)s, %(old_address)s, %(cin_address)s, %(cin_schedule)s, %(dep_schedule)s, %(phone_osmotr)s, %(phone_otvet)s, %(start_date)s,  %(otdel)s
                )
                ON CONFLICT (unom) DO UPDATE SET 
                    old_address = EXCLUDED.old_address, cin_address = EXCLUDED.cin_address, cin_schedule = EXCLUDED.cin_schedule, dep_schedule = EXCLUDED.dep_schedule, phone_osmotr = EXCLUDED.phone_osmotr, 
                    phone_otvet = EXCLUDED.phone_otvet, start_date = EXCLUDED.start_date, otdel = EXCLUDED.otdel 
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