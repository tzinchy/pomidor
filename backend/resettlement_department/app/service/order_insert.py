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
            "Выписка_Серия": "collateral_type"
        }
        order_df.rename(columns=columns_name, inplace=True)

        # Добавляем колонку с извлеченным кодом статьи
        order_df['article_code'] = order_df['accounting_article'].apply(
            lambda x: str(x).split()[0] if pd.notna(x) and len(str(x).split()) > 0 else None
        )
        
        columns_db = list(columns_name.values()) + ['article_code']
        order_df = order_df.dropna(subset=["order_id"])
        order_df = order_df.groupby("order_id").agg(concat_area_id_agg).reset_index()
        order_df = order_df[columns_db]
        
        # Преобразование типов
        order_df["affair_id"] = order_df["affair_id"].astype("Int64")
        order_df["order_id"] = order_df["order_id"].astype("Int64")
        order_df["is_cancelled"] = order_df["is_cancelled"].astype(bool)
        order_df = order_df.replace({np.nan: None})
        
        # Форматирование дат
        date_columns = ["decision_date", "order_date", "cancel_date", 
                       "legal_cancel_date", "order_draft_date"]
        order_df = df_date_to_string(order_df, date_columns)
        order_df = order_df.replace({'None': None})

        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME
        )

        for _, row in order_df.iterrows():
            with connection:
                with connection.cursor() as cursor:
                    # Подготовка значений для вставки
                    values = []
                    for col in columns_db:
                        val = row[col]
                        if isinstance(val, str):
                            val = val.replace("'", "''")
                            values.append(f"'{val}'")
                        elif val is None:
                            values.append("NULL")
                        elif isinstance(val, (dict, list)):
                            values.append(f"'{json.dumps(val)}'")
                        else:
                            values.append(str(val))
                    
                    # SQL для вставки/обновления
                    insert_sql = f"""
                        INSERT INTO public.order_decisions (
                            {", ".join(columns_db)}
                        ) VALUES (
                            {", ".join(values)}
                        )
                        ON CONFLICT (order_id) 
                        DO UPDATE SET 
                            {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
                            updated_at = NOW()
                    """
                    
                    cursor.execute(insert_sql)
                    print(f"DEBUG: Inserted/updated order_id {row['article_code']} {row['order_id']}")

        return 0

    except Exception as e:
        print(f"Error: {e}")
        return e
    finally:
        if connection:
            connection.close()