import psycopg2
import pandas as pd
import numpy as np
from datetime import datetime
from core.config import settings


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
