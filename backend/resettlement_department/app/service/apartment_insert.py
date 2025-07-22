import re

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
                'Сл.инф_APART_ID': 'new_apart_id',
                'Кадастровый номер': 'cad_num',
                'К_Инв/к': 'for_special_needs_marker'
            }
            
            new_apart_df = new_apart_df.rename(columns=rename_new)
            new_apart_df['manual_load_id'] = manual_load_id
            
            # Фильтрация и добавление колонок
            new_apart_required = [
                "district", "municipal_district", "house_address", "floor", "apart_number",
                "full_living_area", "total_living_area", "living_area", "room_count",
                "type_of_settlement", "for_special_needs_marker", "cad_num", "new_apart_id", 
                "manual_load_id"
            ]
            new_apart_df['district'] = new_apart_df['district'].map(district_mapping).fillna(new_apart_df['district'])
            for col in new_apart_required:
                if col not in new_apart_df.columns:
                    new_apart_df[col] = None

            new_apart_values = [tuple(row) for row in new_apart_df[new_apart_required].to_numpy()]
            try:
                execute_values(
                    cursor,
                    f"""INSERT INTO new_apart ({", ".join(new_apart_required)})
                        VALUES %s
                        ON CONFLICT (new_apart_id)
                        DO UPDATE SET 
                            updated_at = NOW()""",
                    new_apart_values
                )
            except Exception as e:
                print(e)

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
                        is_special_needs_marker = EXCLUDED.is_special_needs_marker,
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
            "К_Инв/к": "is_special_needs_marker",
            "КПУ_Снятие_Причина": "removal_reason",
            "КПУ_снятие_сист_ дата": "removal_date",
            "КПУ_Др. напр. закр.": "rsm_another_closed"
        }
        # Формируем список колонок для вставки в базу
        columns_db = list(columns_name.values())
        columns_db.append('is_queue')
        columns_db.append('was_queue')
        columns_db.append('is_hidden')
        columns_db_for_do_update = columns_db.copy()
        columns_db.remove('is_special_needs_marker')
        df.rename(
            columns=columns_name,
            inplace=True,
        )
        # Удаляем строки с пустыми ID
        df = df.dropna(subset=["affair_id"])

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
        df["removal_date"] = df["removal_date"].astype(str)

        # Это поле в базе int
        special_needs_mapping = {"да": 1, "нет": 0}
        df["is_special_needs_marker"] = (
            df["is_special_needs_marker"].map(special_needs_mapping).fillna(0)
        )
        # Добавляем колонку is_queue на основе регулярного выражения
        df["is_queue"] = df["kpu_another"].apply(
              lambda x: 1 if re.search(r"-01-", str(x)) else 0
        ).astype("Int64")
        df["was_queue"] = df["rsm_another_closed"].apply(
              lambda x: 1 if re.search(r"-01-", str(x)) else 0
        ).astype("Int64")
        # На основе removal_reason скрываем некоторые записи
        removal_reason_is_hidden = ["техническое снятие в АСУ", "Ошибочно введенная КПУ","Б/общежитие.Право собственности по суду"]
        df["is_hidden"] = df["removal_reason"].apply(
              lambda x: 1 if x in removal_reason_is_hidden else 0
        ).astype(bool)
        # На основе removal_reason проставляем статус 14 - Подборов не будет
        removal_reason_14 = [
            "п.2 признан ненуждающимся (без предоставления)",
            "Переселение. Жилое помещение свободно",
            "п.2 выкуп комнаты в квартире коммун. заселения",
            "п.7 по личному заявлению очередника",
            "Переселение. Денежная компенсация",
            "Реновация. Денежная компенсация",
            "п.5 выявлены недостоверные документы",
            "п.2 в связи с предоставл.жилья по другому месту постановки",
            "п.2 смерть очередника",
            "Техническое снятие (прошлые года)",
            "Реновация.Без предоставления"
        ]

        #"Б/общежитие.Право собственности по суду", "Ошибочно введенная КПУ", "техническое снятие в АСУ", - кпу не показывать 
        df["status_id"] = df["removal_reason"].apply(
              lambda x: 14 if x in removal_reason_14 else None
        ).astype("Int64")
        # Сокращаем названия округов
        df['district'] = df['district'].map(district_mapping).fillna(df['district'])
        # Удаляем записи на основании округа
        forbidden_districts = ["ДЖП и ЖФ (Газетный пер.,1/12)", "Перовский р-н"]
        df.drop(df[df["district"].isin(forbidden_districts)].index, inplace=True)

        df = df.replace({np.nan: None, "NaT": None})  # "NaT" получается в поле с датой
        df["full_living_area"] = df["full_living_area"].replace({None: 0})
        df["living_area"] = df["living_area"].replace({None: 0})
        df["room_count"] = df["room_count"].replace({None: 0})
        df["people_v_dele"] = df["people_v_dele"].replace({None: 0})
        df["total_living_area"] = df["total_living_area"].replace({None: 0})

        # Важно чтобы порядок колонок в df был такой же как в columns_db
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
            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db_for_do_update)},
            updated_at = NOW()
        """
        # Запрос для обновления справочной информации об успешной выгрузке
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
        # Корректно обновляем справочную информацию о неудачной выгрузке
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
        global district_mapping
        connection = None
        columns_name = {
            "Сл.инф_APART_ID":	"new_apart_id",
            "Адрес_Округ": "district",
            "Адрес_Мун.округ": "municipal_district",
            "Адрес_Короткий": "house_address",
            "Адрес_№ кв": "apart_number",
            "К_Этаж": "floor",
            "К_Комн": "room_count",
            "Площадь общая": "full_living_area",
            "Площадь общая(б/л)": "total_living_area",
            "Площадь жилая": "living_area",
            "Сл.инф_UNOM": "unom",  
            "Сл.инф_UNKV": "un_kv",
            "К_Тип.пл": "apart_type",
            "Распорядитель_Название": "owner",
            "РСМ_Кад номер, квартира": "cad_num",
            "К_Инв/к": "for_special_needs_marker",
            "К_№ подъезда": "entrance_number",
            "Сл.инф_Free_Space_ID": "rsm_apart_id",
        }
        new_apart_df.rename(
            columns=columns_name,
            inplace=True,
        )

        columns_db = list(columns_name.values())


        new_apart_df = new_apart_df[columns_db]

        # Удаляем строки с пустым ID
        new_apart_df = new_apart_df.dropna(subset=["new_apart_id"])

        int_columns = ["new_apart_id", "floor", "unom", "apart_number", "un_kv", "room_count", "rsm_apart_id"]
        for col in int_columns:
            new_apart_df[col] = new_apart_df[col].astype("Int64")
        new_apart_df["total_living_area"] = new_apart_df["total_living_area"].astype(float)
        new_apart_df["full_living_area"] = new_apart_df["full_living_area"].astype(float)
        new_apart_df["living_area"] = new_apart_df["living_area"].astype(float)

        # Сокращаем название округов
        new_apart_df['district'] = new_apart_df['district'].map(district_mapping).fillna(new_apart_df['district'])
        # Это поле в базе int
        special_needs_mapping = {"да": 1, "нет": 0}
        new_apart_df["for_special_needs_marker"] = (
            new_apart_df["for_special_needs_marker"].map(special_needs_mapping).fillna(0)
        )

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
        # нью апарт айди которые не найдены в выгрузке но есть в бд. временно закомментировано
        # existed_df = pd.read_sql("SELECT new_apart_id FROM public.new_apart", connection)
        # existed_apart_ids = existed_df["new_apart_id"]
        # rsm_apart_ids = new_apart_df["new_apart_id"]
        # deleted_rows_ids = existed_apart_ids[~existed_apart_ids.isin(rsm_apart_ids)].values
        # print("Найдено строк отсутствующих в рсм:", len(deleted_rows_ids))

        # placeholder = ",".join(deleted_rows_ids.astype(str))
        # update_status_in_deleted_aparts = f"""
        #     UPDATE new_apart
        #     SET status_id = 14
        #     WHERE new_apart_id IN ({placeholder})
        # """

        insert_data_sql = f"""
            INSERT INTO public.new_apart (
                {", ".join(columns_db)}
            )
            VALUES 
                {args_str}
            ON CONFLICT (new_apart_id) 
            DO UPDATE SET 
            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db if col != "status_id")},
            updated_at = NOW()
        """
        # Проставляем справочную информацию об успешной выгрузке
        set_env_true_sql = """
            UPDATE env.data_updates
            SET success = True,
            updated_at = NOW()
            WHERE name = 'new_aparts_resource'
        """
        with connection:
            with connection.cursor() as cursor:
                print("DEBUG: Connection is open")
                cursor.execute(insert_data_sql)
                # cursor.execute(update_status_in_deleted_aparts)
                print("DEBUG: Data to new_apart is inserted")
                cursor.execute(set_env_true_sql)
                print("DEBUG: Env is set to true")
        out = 0
    except Exception as e:
        out = e
        print(e)
        print("DEBUG: Exception occurred")
        # Проставляем справочную информацию о неудачной выгрузке
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
