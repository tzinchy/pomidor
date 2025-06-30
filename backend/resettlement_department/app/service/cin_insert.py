import pandas as pd
from repository.database import get_db_connection


def insert_cin(cin_df : pd.DataFrame) -> int:
    connection = get_db_connection() 
    cursor = connection.cursor()

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
            })

        # Вставка данных
        for data in data_to_insert:
            cursor.execute(
                """INSERT INTO cin (
                    unom, old_address, cin_address, cin_schedule, 
                    dep_schedule, phone_osmotr, phone_otvet, 
                    start_date, otdel
                ) VALUES (
                    %(unom)s, %(old_address)s, %(cin_address)s, 
                    %(cin_schedule)s, %(dep_schedule)s, %(phone_osmotr)s, 
                    %(phone_otvet)s, %(start_date)s, %(otdel)s
                )
                ON CONFLICT (unom) DO UPDATE SET 
                    updated_at = NOW()""",
                data
            )

    connection.commit()
    return 200