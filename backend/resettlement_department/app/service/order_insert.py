import json

import numpy as np
import pandas as pd
import psycopg2
from core.config import settings


def df_date_to_string(df: pd.DataFrame, columns):
    for col in columns:
        df[col] = df[col].astype(str)
    return df

# Эта агрегирующая функция для датафрейма выписки.
# Она принимает датафрейм, где колонка area_id не словарь,
# затем объединяет повторяющиеся и неповторяющиеся значения в словарь
# NaN значения эта штука должна не трогать
def concat_area_id_agg(series: pd.Series):
    if series.name != "area_id":
        return series.iloc[0]
    if len(series) > 1:
        out = {}
        for i, v in enumerate(series):
            if pd.notna(v):
                out[str(i)] = int(v)
        if not out:
            return None
        return out
    else:
        return series.apply(lambda x: {"0": int(x)} if pd.notna(x) else x)


def insert_data_to_order_decisions(order_df: pd.DataFrame):
    try:
        connection = None
        columns_name = {
            "КПУ_Дело_Идентификатор": "affair_id",
            "Идентификатор выписки": "order_id",
            "Выписка_Решение_Д": "decision_date",
            "Выписка_Решение №": "decision_number",
            "Выписка_Д": "order_date",
            "Выписка_Аннулирована": "is_cancelled",
            "Выписка_Аннулирование_Дата": "cancel_date",
            "Выписка_Аннулирование_Дата_РД": "legal_cancel_date",
            "Выписка_Аннулирование_Номер_РД": "legal_order_id",
            "Выписка_Аннулирование_Причина": "cancel_reason",
            "Выписка_ид_площади": "area_id",
            "Дата создания проекта выписки": "order_draft_date",
            "Выписка_Статья учета": "accounting_article",
            "Выписка_причина предоставления": "legal_reason",
            "Выписка_Серия": "collateral_type",
        }
        order_df.rename(
            columns=columns_name,
            inplace=True,
        )

        columns_db = list(columns_name.values())
        order_df = order_df.dropna(subset=["order_id"])

        order_df = order_df.groupby("order_id").agg(concat_area_id_agg).reset_index()
        order_df = order_df[columns_db]
        order_df["affair_id"] = order_df["affair_id"].astype("Int64")
        order_df["order_id"] = order_df["order_id"].astype("Int64")
        order_df["is_cancelled"] = order_df["is_cancelled"].astype(bool)

        # Заменяем NaN на None (для PostgreSQL)
        order_df = order_df.replace({np.nan: None})

        order_df = df_date_to_string(order_df, 
            ["decision_date", "order_date", "cancel_date", "legal_cancel_date", "order_draft_date"]
        )
        order_df = order_df.replace({'None': None})

        # Преобразуем в список кортежей для вставки
        args = order_df.itertuples(index=False, name=None)
        args_str = ",".join(
            "({})".format(
                ", ".join(
                    "'{}'".format(x.replace("'", "''")) if isinstance(x, str)
                    else "NULL" if x is None
                    else "'{}'".format(json.dumps(x).replace("'", "''")) if isinstance(x, dict)
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
            INSERT INTO public.order_decisions (
                {", ".join(columns_db)}
            )
            VALUES 
                {args_str}
            ON CONFLICT (order_id) 
            DO UPDATE SET 
            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
            updated_at = NOW()
        """
        out = 0
        with connection:
            with connection.cursor() as cursor:
                print("DEBUG: Data is inserted")
                cursor.execute(insert_data_sql)
    except Exception as e:
        out = e
        print(e)
    finally:
        if connection:
            connection.close()
        return out