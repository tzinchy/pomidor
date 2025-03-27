import numpy as np
import pandas as pd
import psycopg2
from core.config import settings
from service.apartment_insert import format_datetime_columns


def df_date_to_string(df: pd.DataFrame, columns):
    for col in columns:
        df[col] = df[col].astype(str)
    return df


def insert_data_to_extract_decisions(extract_df: pd.DataFrame):
    # try:
        connection = None
        columns_name = {
            "КПУ_Дело_Идентификатор": "case_id",
            "Идентификатор выписки": "extract_id",
            "Выписка_Решение_Д": "decision_date",
            "Выписка_Решение №": "decision_number",
            "Выписка_Д": "extract_date",
            "Выписка_Аннулирована": "is_cancelled",
            "Выписка_Аннулирование_Дата": "cancel_date",
            "Выписка_Аннулирование_Дата_РД": "legal_cancel_date",
            "Выписка_Аннулирование_Номер_РД": "legal_extract_id",
            "Выписка_Аннулирование_Причина": "cancel_reason",
            "Выписка_ид_площади": "area_id",
            "Дата создания проекта выписки": "extract_draft_date",
        }
        extract_df.rename(
            columns=columns_name,
            inplace=True,
        )
        columns_db = list(columns_name.values())
        extract_df = extract_df[columns_db]
        extract_df = extract_df.dropna(subset=["extract_id"])

        extract_df["case_id"] = extract_df["case_id"].astype("Int64")
        extract_df["extract_id"] = extract_df["extract_id"].astype("Int64")
        extract_df["area_id"] = extract_df["area_id"].astype("Int64")
        extract_df["is_cancelled"] = extract_df["is_cancelled"].astype(bool)

        # Заменяем NaN на None (для PostgreSQL)
        extract_df = extract_df.replace({np.nan: None})

        extract_df = df_date_to_string(extract_df, 
                               ["decision_date", "extract_date", "cancel_date", "legal_cancel_date", "extract_draft_date"]
                               )
        extract_df = extract_df.replace({'None': None})

        # Преобразуем в список кортежей для вставки
        args = extract_df.itertuples(index=False, name=None)
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
            INSERT INTO public.extract_decisions (
                {", ".join(columns_db)}
            )
            VALUES 
                {args_str}
            ON CONFLICT (extract_id) 
            DO UPDATE SET 
            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
            updated_at = NOW()
        """
        out = 0
        with connection:
            with connection.cursor() as cursor:
                print(-3)
                cursor.execute(insert_data_sql)
    # except Exception as e:
    #     out = e
    #     print(e)
    # finally:
        if connection:
            connection.close()
        return out