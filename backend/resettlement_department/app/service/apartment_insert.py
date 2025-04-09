import re
from datetime import datetime

import numpy as np
import pandas as pd
import psycopg2
from core.config import settings
from psycopg2.extras import execute_values

district_mapping = {
    "Восточный АО": "ВАО",
    "Центральный АО": "ЦАО",
    "Северо-Восточный АО": "СВАО",
    "Новомосковский АО": "НАО",
    "Люблинский р-н": "ЮВАО",  # Люблинский район относится к Юго-Восточному АО
    "Юго-Восточный АО": "ЮВАО",
    "Северо-Западный АО": "СЗАО",
    "Северный АО": "САО",
    "Зеленоградский АО": "ЗелАО",
    "Юго-Западный АО": "ЮЗАО",
    "Южный АО": "ЮАО",
    "Вос": "ВАО",
    "СЗАО": "СЗАО",
    "Троицкий АО": "ТАО",
    "Западный АО": "ЗАО",
    "Зел": "ЗелАО",
    "С-В": "СВАО",
    "Южн": "ЮАО",
    "С-З": "СЗАО",
    "Зап": "ЗАО",
    "Цен": "ЦАО",
    "Ю-З": "ЮЗАО",
    "ТАО": "ТАО",
    "Сев": "САО",
    "НАО": "НАО",
    "МО": "МО",  # Московская область, если нужно
    "Ю-В": "ЮВАО",
    "Якиманка": "ЦАО",  # Район в ЦАО
    "Тверской": "ЦАО",  # Район в ЦАО
    "Северное Бутово": "ЮЗАО",  # Район в ЮЗАО
    "Очаково-Матвеевское": "ЗАО",  # Район в ЗАО
    "Левобережный": "САО",  # Район в САО
    "Некрасовка": "ЮВАО",  # Район в ЮВАО
    "Митино": "СЗАО",  # Район в СЗАО
    "Крылатское": "ЗАО",  # Район в ЗАО
    "Бирюлёво Восточное": "ЮАО",  # Район в ЮАО
    "Академический": "ЮЗАО"  # Район в ЮЗАО
}

def insert_data_to_old(df):
    global district_mapping
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
                "409866": "rsm_notes",
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
        old_apart['district'] = old_apart['district'].map(district_mapping).fillna(old_apart['district'])
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
                "rsm_notes",
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
                people_in_family, cad_num, rsm_notes, district, municipal_district, house_address, 
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
                rsm_notes = EXCLUDED.rsm_notes,
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
    global district_mapping
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
        int_columns = ["new_apart_id", "building_id", "floor", "rsm_id", "room_count", "un_kv"]
        for column in int_columns:
            new_apart_df[column] = new_apart_df[column].astype(int)
        # new_apart_df['apart_number'] = new_apart_df['apart_number'].astype('str')
        new_apart_df['district'] = new_apart_df['district'].map(district_mapping).fillna(new_apart_df['district'])
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
            sentence_number, selection_action, conditions, rsm_notes, claim, 
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
            rsm_notes = EXCLUDED.rsm_notes,
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


def insert_to_db(new_apart_df, old_apart_df, cin_df, file_name, file_path):
    global district_mapping
    connection = psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME
    )
    cursor = connection.cursor()

    try:
        # 1. Вставка в manual_load с обработкой конфликтов
        is_new_apart = not new_apart_df.empty
        is_old_apart = not old_apart_df.empty
        is_cin = not cin_df.empty

        cursor.execute(
            """INSERT INTO manual_load 
                (filename, is_old_apart, is_new_apart, is_cin, file_path) 
             VALUES (%s, %s, %s, %s, %s)
             ON CONFLICT (filename) DO UPDATE SET
                 is_old_apart = EXCLUDED.is_old_apart,
                 is_new_apart = EXCLUDED.is_new_apart,
                 is_cin = EXCLUDED.is_cin,
                 file_path = EXCLUDED.file_path,
                 updated_at = NOW()
             RETURNING manual_load_id""",
            (file_name, is_old_apart, is_new_apart, is_cin, file_path)
        )
        manual_load_id = cursor.fetchone()[0]

        # 2. Обработка new_apart
        if not new_apart_df.empty:
            new_apart_df['К_Инв/к'] = new_apart_df['К_Инв/к'].astype(str).str.lower()
            new_apart_df['К_Инв/к'] = new_apart_df['К_Инв/к'].apply(lambda x: 1 if 'да' in x else 0)
            
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
            
            new_apart_df = new_apart_df.rename(columns=rename_new)
            new_apart_df['manual_load_id'] = manual_load_id
            
            # Фильтрация и добавление колонок
            new_apart_required = [
                "district", "municipal_district", "house_address", "floor", "apart_number",
                "full_living_area", "total_living_area", "living_area", "room_count",
                "type_of_settlement", "for_special_needs_marker", "cad_num", "up_id", 
                "manual_load_id"
            ]
            new_apart_df['district'] = new_apart_df['district'].map(district_mapping).fillna(new_apart_df['district'])
            for col in new_apart_required:
                if col not in new_apart_df.columns:
                    new_apart_df[col] = None

            new_apart_values = [tuple(row) for row in new_apart_df[new_apart_required].to_numpy()]
            
            execute_values(
                cursor,
                f"""INSERT INTO new_apart ({", ".join(new_apart_required)})
                    VALUES %s
                    ON CONFLICT (up_id)
                    DO UPDATE SET 
                        {", ".join([f"{col} = EXCLUDED.{col}" for col in new_apart_required if col != 'up_id'])},
                        updated_at = NOW()""",
                new_apart_values
            )

        # 3. Обработка old_apart
        if not old_apart_df.empty:
            rename_old = {
                'Округ': 'district',
                'район': 'municipal_district',
                'ФИО': 'fio',
                'адрес дома': 'house_address',
                '№ кв-ры': 'apart_number',
                'Вид засел.': 'type_of_settlement',
                'тип кв-ры': 'apart_type',
                'кол-во комнат': 'room_count',
                'площ. жил. пом.': 'full_living_area',
                'общ. пл.': 'total_living_area',
                'жил. пл.': 'living_area',
                'Кол-во членов семьи': 'people_v_dele',
                'Потребность': 'is_special_needs_marker',
                'мин этаж': 'min_floor',
                'макс этаж': 'max_floor',
                'Дата покупки': 'buying_date',
                'ID': 'affair_id'
            }
            
            old_apart_df = old_apart_df.rename(columns=rename_old)
            old_apart_df['manual_load_id'] = manual_load_id
            
            # Обработка даты
            if 'buying_date' in old_apart_df.columns:
                old_apart_df['buying_date'] = pd.to_datetime(old_apart_df['buying_date'], errors='coerce')
                old_apart_df['buying_date'] = old_apart_df['buying_date'].apply(lambda x: x if pd.notnull(x) else None)

            # Фильтрация колонок
            old_apart_required = [
                "affair_id", "kpu_number", "fio", "surname", "firstname", "lastname",
                "people_in_family", "category", "cad_num", "rsm_notes", "documents", "district",
                "house_address", "apart_number", "room_count", "floor", "full_living_area",
                "living_area", "people_v_dele", "people_uchet", "total_living_area", "apart_type",
                "manipulation_notes", "municipal_district", "is_special_needs_marker", "min_floor",
                "max_floor", "buying_date", "type_of_settlement", "history_id", 
                "kpu_another", "manual_load_id"
            ]
            old_apart_df['district'] = old_apart_df['district'].map(district_mapping).fillna(old_apart_df['district'])
            for col in old_apart_required:
                if col not in old_apart_df.columns:
                    old_apart_df[col] = None

            old_apart_values = [tuple(row) for row in old_apart_df[old_apart_required].to_numpy()]
            
            execute_values(
                cursor,
                f"""INSERT INTO old_apart ({", ".join(old_apart_required)})
                    VALUES %s
                    ON CONFLICT (affair_id)
                    DO UPDATE SET 
                        {", ".join([f"{col} = EXCLUDED.{col}" for col in old_apart_required if col != 'affair_id'])},
                        updated_at = NOW()""",
                old_apart_values
            )
        
        # 4. Обработка CIN
        if not cin_df.empty:
            # Подготовка данных
            data_to_insert = []
            cin_df["Дата начала работы"] = pd.to_datetime(cin_df["Дата начала работы"], errors="coerce").dt.date
            
            for _, row in cin_df.iterrows():
                data_to_insert.append({
                    "unom": str(row["УНОМ"]),
                    "old_address": str(row["Адрес отселения"]),
                    "cin_address": str(row["Адрес ЦИНа"]),
                    "cin_schedule": str(row["График работы ЦИН"]),
                    "dep_schedule": str(row["График работы Департамента в ЦИНе"]),
                    "phone_osmotr": str(row["Телефон для осмота"]) if pd.notna(row["Телефон для осмота"]) else None,
                    "phone_otvet": str(row["Телефон для ответа"]) if pd.notna(row["Телефон для ответа"]) else None,
                    "start_date": row["Дата начала работы"] if pd.notna(row["Дата начала работы"]) else None,
                    "otdel": str(row["Адрес Отдела"]),
                    "manual_load_id": manual_load_id
                })

            # Вставка данных
            for data in data_to_insert:
                cursor.execute(
                    """INSERT INTO cin (
                        unom, old_address, cin_address, cin_schedule, 
                        dep_schedule, phone_osmotr, phone_otvet, 
                        start_date, otdel, manual_load_id
                    ) VALUES (
                        %(unom)s, %(old_address)s, %(cin_address)s, 
                        %(cin_schedule)s, %(dep_schedule)s, %(phone_osmotr)s, 
                        %(phone_otvet)s, %(start_date)s, %(otdel)s, %(manual_load_id)s
                    )
                    ON CONFLICT (unom) DO UPDATE SET 
                        old_address = EXCLUDED.old_address,
                        cin_address = EXCLUDED.cin_address,
                        cin_schedule = EXCLUDED.cin_schedule,
                        dep_schedule = EXCLUDED.dep_schedule,
                        phone_osmotr = EXCLUDED.phone_osmotr,
                        phone_otvet = EXCLUDED.phone_otvet,
                        start_date = EXCLUDED.start_date,
                        otdel = EXCLUDED.otdel,
                        manual_load_id = EXCLUDED.manual_load_id,
                        updated_at = NOW()""",
                    data
                )

        connection.commit()
        return manual_load_id

    except Exception as e:
        connection.rollback()
        print(e)
        raise e
    finally:
        cursor.close()
        connection.close()

def insert_data_to_old_apart(df: pd.DataFrame):
    try:
        global district_mapping
        connection = None

        columns_name = {
            "Идентификатор дела": "affair_id",
            "КПУ_Дело_№ полный(новый)": "kpu_number",
            "КПУ_ФИО": "fio",
            "КПУ_Заявитель_Фамилия": "surname",
            "КПУ_Заявитель_Имя": "firstname",
            "КПУ_Заявитель_Отчество": "lastname",
            "КПУ_Чел.в семье": "people_in_family",
            "КПУ_Направление_код": "category",
            "КПУ_кадастровый_номер_адреса": "cad_num",
            "КПУ_Примечание": "rsm_notes",
            "Адрес_Округ": "district",
            "Адрес_Район": "municipal_district",
            "Адрес_Короткий": "house_address",
            "Адрес_№ кв": "apart_number",
            "К_Комн": "room_count",
            "К_Этаж": "floor",
            "К_Общ": "full_living_area",
            "К_Жил": "living_area",
            "КПУ_Чел.в деле": "people_v_dele",
            "КПУ_Чел.учете": "people_uchet",
            "К_Общ(б/л)": "total_living_area",
            "К_Тип_Кв": "apart_type",
            "КПУ_Др. напр. откр.": "kpu_another",
            "КПУ_Вид засел.": "type_of_settlement",
            "КПУ_Состояние": "rsm_status",
            "К_Инв/к": "is_special_needs_marker"
        }
        columns_db = list(columns_name.values())
        columns_db.append('is_queue')
        df.rename(
            columns=columns_name,
            inplace=True,
        )
        # Удаляем строки с пустыми ID
        df = df.dropna(subset=["affair_id"])
        special_needs_mapping = {"да": 1, "нет": 0}
        df["is_special_needs_marker"] = (
            df["is_special_needs_marker"].map(special_needs_mapping).fillna(0)
        )

        df["affair_id"] = df["affair_id"].astype("Int64")
        df["people_in_family"] = df["people_in_family"].astype("Int64")
        df["category"] = df["category"].astype("Int64")
        df["room_count"] = df["room_count"].astype("Int64")
        df["floor"] = df["floor"].astype("Int64")
        df["total_living_area"] = df["total_living_area"].astype(float)
        df["living_area"] = df["living_area"].astype(float)
        df["people_v_dele"] = df["people_v_dele"].astype("Int64")
        df["people_uchet"] = df["people_uchet"].astype("Int64")
        df["full_living_area"] = df["full_living_area"].astype(float)

        # Добавляем колонку is_queue на основе регулярного выражения
        df["is_queue"] = df["kpu_another"].apply(
              lambda x: 1 if re.search(r"-01-", str(x)) else 0
        ).astype("Int64")

        df['district'] = df['district'].map(district_mapping).fillna(df['district'])

        df = df.replace({np.nan: None})
        df["full_living_area"] = df["full_living_area"].replace({None: 0})
        df["living_area"] = df["living_area"].replace({None: 0})
        df["room_count"] = df["room_count"].replace({None: 0})
        df["people_v_dele"] = df["people_v_dele"].replace({None: 0})
        df["total_living_area"] = df["total_living_area"].replace({None: 0})

        df = df[columns_db]

        args = df.itertuples(index=False, name=None)
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

        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )
        insert_data_sql = f"""
            INSERT INTO public.old_apart (
                {", ".join(columns_db)}
            )
            VALUES 
                {args_str}
            ON CONFLICT (affair_id) 
            DO UPDATE SET 
            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
            updated_at = NOW()
        """
        set_env_true_sql = """
            UPDATE env.data_updates
            SET success = True,
            updated_at = NOW()
            WHERE name = 'old_aparts_kpu'
        """
        out = 0
        with connection:
            with connection.cursor() as cursor:
                print("DEBUG: Connection is open")
                cursor.execute(insert_data_sql)
                print("DEBUG: Data to old_apart is inserted")
                cursor.execute(set_env_true_sql)
                print("DEBUG: Env is set to true")
    except Exception as e:
        out = e
        print(e)
        print("DEBUG: Exception occurred")
        if not connection:
            print("DEBUG: Connection is None. Creating new one")
            connection = psycopg2.connect(
                host=settings.project_management_setting.DB_HOST,
                user=settings.project_management_setting.DB_USER,
                password=settings.project_management_setting.DB_PASSWORD,
                port=settings.project_management_setting.DB_PORT,
                database=settings.project_management_setting.DB_NAME
            )
        with connection:
            with connection.cursor() as cursor:
                print("DEBUG: Connection is open in except block")
                set_env_false_sql = """
                    UPDATE env.data_updates
                    SET success = False,
                    updated_at = NOW()
                    WHERE name = 'old_aparts_kpu'
                """
                cursor.execute(set_env_false_sql)
    finally:
        print("DEBUG: finally block")
        if connection:
            print("DEBUG: connection found and closed")
            connection.close()
        return out
    
def insert_data_to_new_apart(new_apart_df: pd.DataFrame):
    try:
        print(new_apart_df.columns)
        global district_mapping
        connection = None
        columns_name = {
            "Сл.инф_APART_ID":	"rsm_apart_id",
            "Адрес_Округ": "district",
            "Адрес_Мун.округ": "municipal_district",
            "Адрес_Короткий": "house_address",
            "Адрес_№ кв": "apart_number",
            "К_Этаж": "floor",
            "К_Комн": "room_count",
            "Площадь общая": "full_living_area",
            "Площадь общая(б/л)": "total_living_area",
            "Площадь жилая": "living_area",
            "Сл.инф_UNOM": "building_id",  
            "Сл.инф_UNKV": "un_kv",
            "К_Тип.пл": "apart_type",
            "Распорядитель_Название": "owner",
            "РСМ_Кад номер, квартира": "apart_kad_number",
            "РСМ, Кад номер, комната": "room_kad_number",
            "К_Инв/к": "for_special_needs_marker",
            "К_№ подъезда": "entrance_number",
            "Идентификатор площади": "new_apart_id",
        }
        new_apart_df.rename(
            columns=columns_name,
            inplace=True,
        )
        columns_db = list(columns_name.values())
        new_apart_df = new_apart_df[columns_db]
        new_apart_df = new_apart_df.dropna(subset=["new_apart_id"])
        special_needs_mapping = {"да": 1, "нет": 0}
        new_apart_df["for_special_needs_marker"] = (
            new_apart_df["for_special_needs_marker"].map(special_needs_mapping).fillna(0)
        )

        int_columns = ["new_apart_id", "floor", "building_id", "apart_number", "un_kv", "room_count", "area_id"]
        for col in int_columns:
            new_apart_df[col] = new_apart_df[col].astype("Int64")
        new_apart_df["total_living_area"] = new_apart_df["total_living_area"].astype(float)
        new_apart_df["full_living_area"] = new_apart_df["full_living_area"].astype(float)
        new_apart_df["living_area"] = new_apart_df["living_area"].astype(float)

        new_apart_df['district'] = new_apart_df['district'].map(district_mapping).fillna(new_apart_df['district'])

        new_apart_df = new_apart_df.replace({np.nan: None})
        new_apart_df["full_living_area"] = new_apart_df["full_living_area"].replace({None: 0})
        new_apart_df["living_area"] = new_apart_df["living_area"].replace({None: 0})
        new_apart_df["room_count"] = new_apart_df["room_count"].replace({None: 0})
        new_apart_df["total_living_area"] = new_apart_df["total_living_area"].replace({None: 0})

        # Преобразуем в список кортежей для вставки
        args = new_apart_df.itertuples(index=False, name=None)
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

        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )

        insert_data_sql = f"""
            INSERT INTO public.new_apart (
                {", ".join(columns_db)}
            )
            VALUES 
                {args_str}
            ON CONFLICT (new_apart_id) 
            DO UPDATE SET 
            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
            updated_at = NOW()
        """
        set_env_true_sql = """
            UPDATE env.data_updates
            SET success = True,
            updated_at = NOW()
            WHERE name = 'new_aparts_resource'
        """
        out = 0
        with connection:
            with connection.cursor() as cursor:
                print("DEBUG: Connection is open")
                cursor.execute(insert_data_sql)
                print("DEBUG: Data to new_apart is inserted")
                cursor.execute(set_env_true_sql)
                print("DEBUG: Env is set to true")
    except Exception as e:
        out = e
        print(e)
        print("DEBUG: Exception occurred")
        if not connection:
            print("DEBUG: Connection is None. Creating new one")
            connection = psycopg2.connect(
                host=settings.project_management_setting.DB_HOST,
                user=settings.project_management_setting.DB_USER,
                password=settings.project_management_setting.DB_PASSWORD,
                port=settings.project_management_setting.DB_PORT,
                database=settings.project_management_setting.DB_NAME
            )
        with connection:
            with connection.cursor() as cursor:
                print("DEBUG: Connection is open in except block")
                set_env_false_sql = """
                    UPDATE env.data_updates
                    SET success = False,
                    updated_at = NOW()
                    WHERE name = 'new_aparts_resource'
                """
                cursor.execute(set_env_false_sql)
    finally:
        if connection:
            connection.close()
        return out
