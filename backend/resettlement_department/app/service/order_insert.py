import json

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import errors
from core.config import settings


def create_stable_area_id_repr(area_id_val):
    """
    Создает стабильное строковое представление для area_id (словарь или JSON-строка).
    Возвращает отсортированную JSON-строку или None/строку в случае ошибки/не словаря.
    """
    if pd.isna(area_id_val):
        return None

    dict_data = None
    try:
        # Если это уже словарь
        if isinstance(area_id_val, dict):
            dict_data = area_id_val
        # Если это строка (потенциально JSON)
        elif isinstance(area_id_val, str):
            try:
                # Пытаемся распарсить как JSON
                dict_data = json.loads(area_id_val)
                # Убедимся, что результат парсинга - словарь
                if not isinstance(dict_data, dict):
                    # Если распарсилось не в словарь, возвращаем исходную строку
                    print(f"Warning: Parsed area_id is not a dict: {area_id_val}")
                    return f"NOT_DICT_{area_id_val}"
            except json.JSONDecodeError:
                # Если это невалидный JSON, возвращаем исходную строку как есть
                print(f"Warning: area_id is not valid JSON: {area_id_val}")
                return f"INVALID_JSON_{area_id_val}"
        # Если это что-то другое (не строка, не словарь, не None)
        else:
            # Просто преобразуем в строку
            return str(area_id_val)

        # Если успешно получили словарь (dict_data)
        if isinstance(dict_data, dict):
            # Сериализуем в JSON с сортировкой ключей
            return json.dumps(dict_data, sort_keys=True, ensure_ascii=False, separators=(',', ':'))
        else:
            # Этот блок не должен сработать из-за проверок выше, но на всякий случай
             return str(area_id_val) # Fallback

    except Exception as e:
        print(f"Error creating stable area_id repr for {area_id_val}: {e}")
        # В случае любой другой ошибки, возвращаем просто строку
        return str(area_id_val)


def df_date_to_string(df: pd.DataFrame, columns):
    for col in columns:
        df[col] = pd.to_datetime(df[col], errors='coerce')
        df[col] = df[col].dt.date.astype(str)
        df[col] = df[col].replace("NaT", None)
    return df

# Эта агрегирующая функция для датафрейма выписки.
# Она принимает датафрейм, где колонка area_id не словарь,
# затем объединяет повторяющиеся и неповторяющиеся значения в словарь
# NaN значения эта штука должна не трогать
def concat_area_id_agg(series: pd.Series):
    if series.name != "area_id":
        return series.iloc[0]
    
    # Собираем уникальные area_id (игнорируя NaN)
    unique_ids = set(series.dropna().astype(int).unique())
    
    if not unique_ids:
        return None
    else:
        # Создаем словарь где ключи - это area_id, а значения - 1 (или можно использовать True)
        return {str(area_id): {} for area_id in unique_ids}

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

        # Загружаем только изменяющиеся значения
        existed_df = pd.read_sql("SELECT * FROM public.order_decisions", connection)
        existed_df = existed_df[columns_db]
        existed_df = df_date_to_string(existed_df, date_columns)
        existed_df = existed_df.replace({'None': None})
        existed_df["area_id_str"] = existed_df["area_id"].apply(create_stable_area_id_repr)
        order_df["area_id_str"] = order_df["area_id"].apply(create_stable_area_id_repr)

        key_col = 'order_id'
        comparison_cols = list((set(columns_db) - {key_col, "area_id"}) | {"area_id_str"})
        print(f"Колонки для сравнения изменений: {comparison_cols}")
        order_df_subset = order_df[[key_col] + comparison_cols].copy()
        existed_df_subset = existed_df[[key_col] + comparison_cols].copy()
        merged_df = order_df_subset.merge(
            existed_df_subset,
            on=key_col,
            how='outer', # outer чтобы найти и новые, и удаленные (если нужно)
            suffixes=('_new', '_old'),
            indicator=True # Добавляет '_merge'
        )
        new_rows_idx = merged_df[merged_df['_merge'] == 'left_only'].index
        new_order_ids = merged_df.loc[new_rows_idx, key_col].tolist()
        print(f"Найдено новых строк для вставки: {len(new_order_ids)}")
        both_rows_idx = merged_df[merged_df['_merge'] == 'both'].index
        rows_to_check = merged_df.loc[both_rows_idx].copy()
        print(f"Найдено строк для проверки на изменения: {len(rows_to_check)}")
        diff_mask_combined = pd.Series(False, index=rows_to_check.index)
        for col in comparison_cols: # Используем исходные имена колонок
            col_new = f'{col}_new'
            col_old = f'{col}_old'

            if col_new in rows_to_check and col_old in rows_to_check:
                # Сравнение с корректной обработкой NA/None
                # (A == B) or (A is NA and B is NA)
                are_equal = rows_to_check[col_new].eq(rows_to_check[col_old]) | \
                            (rows_to_check[col_new].isna() & rows_to_check[col_old].isna())
                # Инвертируем маску, чтобы True означало "есть различие"
                has_diff = ~are_equal
                diff_mask_combined = diff_mask_combined | has_diff
            else:
                print(f"Предупреждение: Колонка {col} (_new/_old) не найдена для сравнения.")
        changed_rows_to_update = rows_to_check[diff_mask_combined]
        changed_order_ids = changed_rows_to_update[key_col].tolist()
        print(f"Найдено измененных строк для обновления: {len(changed_order_ids)}")
        ids_to_process = set(new_order_ids) | set(changed_order_ids)
        print(f"Всего строк для обработки (INSERT/UPDATE): {len(ids_to_process)}")
        df_to_process = order_df[order_df[key_col].isin(ids_to_process)].copy()
        print(f"Запуск вставки/обновления для {len(df_to_process)} строк...")

        existed_affair_ids = pd.read_sql("SELECT affair_id FROM public.old_apart", connection)
        existed_affair_ids = existed_affair_ids["affair_id"].astype("Int64")
        df_to_process = df_to_process[df_to_process["affair_id"].isin(existed_affair_ids)]
        print(f"После отсечения по внешнему ключу affair_id осталось {len(df_to_process)}")

        total = len(df_to_process)
        i = 1
        for _, row in df_to_process.iterrows():
            print(f"Row {i}; total {total}")
            i += 1
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
        raise e
    finally:
        if connection:
            connection.close()