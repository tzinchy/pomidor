import json

import numpy as np
import pandas as pd
import psycopg2
from psycopg2 import errors
from tqdm import tqdm

from app.core.config import settings


# нигде не используется
def concat_new_apart_id_agg(series: pd.Series):
    if series.name != "new_apart_id":
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


def combine_new_apart_id_and_decline_reason_id(row: pd.Series):
    if row["Претензия"]:
        return {str(row["new_apart_id"]): {"status_id": 2, "decline_reason_id": None}}
    else:
        return {str(row["new_apart_id"]): {"status_id": 7}}


def insert_data_to_offer(df: pd.DataFrame):
    try:
        connection = None
        # Колонки для таблицы offer
        columns_offer_name = {
            "Идентификатор дела": "affair_id",
            "Идентификатор площади": "new_apart_id",
            "Исх. № предложения": "outgoing_offer_number",
            "Дата предложения": "offer_date",
        }
        columns_db = ["affair_id", "new_aparts", "outgoing_offer_number", "offer_date"]
        # Колонки для таблицы decline_reason
        columns_decline_name = {
            "Претензия": "notes",
        }
        df.rename(columns=columns_offer_name, inplace=True)
        df.rename(columns=columns_decline_name, inplace=True)

        # Преобразование типов
        # Какое-то хитрое преобразование, чтобы обработать нечисловые значения
        df["affair_id"] = pd.to_numeric(df["affair_id"], errors="coerce")
        df["offer_date"] = df["offer_date"].astype(str)
        df["affair_id"] = df["affair_id"].astype("Int64")
        df["new_apart_id"] = df["new_apart_id"].astype("Int64")

        # Удаляем записи с пустыми полями
        df = df.dropna(subset=["affair_id", "new_apart_id"])
        df = df.replace({np.nan: None, "00:00:00": None})

        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME,
        )

        cursor = connection.cursor()
        for _, row in tqdm(df.iterrows(), miniters=50, total=len(df)):
            try:
                # Формируем поле json new_aparts. 
                # Добавляем причину отказа при отказе
                # NOTE: Каждый раз добавляет новую причину отказа 
                #       вместо проверки существует ли уже такая
                if row["notes"]:
                    cursor.execute(f"""
                        INSERT INTO public.decline_reason(notes) VALUES ('{row["notes"]}')
                        RETURNING decline_reason_id;
                    """)
                    decline_reason_id = cursor.fetchone()[0]
                    row["new_aparts"] = {
                        str(row["new_apart_id"]): {
                            "status_id": 2,
                            "decline_reason_id": decline_reason_id,
                        }
                    }
                else:
                    row["new_aparts"] = {str(row["new_apart_id"]): {"status_id": 7}}
                values = []
                # Формируем значения для вставки
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
                # Перед вставкой новой записи 
                # необходимо у предыдущих подборов проставить отказ
                cursor.execute(f"""
                    UPDATE offer
                    SET
                        status_id = 2,
                        new_aparts = (
                            SELECT
                                COALESCE(
                                    jsonb_object_agg(
                                        key, 
                                        jsonb_set(
                                            value, 
                                            '{{status_id}}', 
                                            to_jsonb(2)
                                        )
                                    ), 
                                    '{{}}'::jsonb
                                )
                            FROM
                                jsonb_each(COALESCE(offer.new_aparts, '{{}}'::jsonb))
                        ),
                        updated_at = NOW()
                    WHERE
                        offer_id IN (
                            SELECT
                                MAX(offer_id)
                            FROM
                                offer
                            WHERE
                                affair_id = {row["affair_id"]}
                            GROUP BY
                                affair_id
                        );

                    INSERT INTO public.offer (
                        {", ".join(columns_db)}
                    ) VALUES {"({})".format(",".join(values))}
                """)
                connection.commit()
            except errors.ForeignKeyViolation:
                connection.rollback()
            except Exception as e:
                connection.rollback()
                raise e

    except Exception as e:
        raise e
    finally:
        if connection:
            connection.close()


def update_new_apart_ids(df: pd.DataFrame):
    try:
        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME,
        )

        cursor = connection.cursor()

        # Подготовка данных
        df = df.rename(
            columns={
                "Идентификатор площади": "new_apart_id",
                "Исх. № предложения": "outgoing_offer_number",
            }
        )

        df["new_apart_id"] = df["new_apart_id"].astype(str)  # Ключ JSON всегда строка
        df["outgoing_offer_number"] = df["outgoing_offer_number"].astype(str)

        for _, row in tqdm(df.iterrows(), total=len(df)):
            try:
                # Получаем текущий JSON из БД
                cursor.execute(
                    """
                    SELECT new_aparts FROM offer 
                    WHERE outgoing_offer_number = %s
                """,
                    (row["outgoing_offer_number"],),
                )

                current_json = cursor.fetchone()[0]

                if not current_json:
                    continue  # Пропускаем, если JSON пуст

                # Извлекаем первое (и единственное) значение из JSON
                old_key = next(iter(current_json.keys()))
                json_value = current_json[old_key]

                # Создаем новый JSON с новым ключом и старым значением
                new_json = {row["new_apart_id"]: json_value}

                # Обновляем запись в БД
                cursor.execute(
                    """
                    UPDATE offer 
                    SET new_aparts = %s,
                        updated_at = NOW()
                    WHERE outgoing_offer_number = %s
                """,
                    (json.dumps(new_json), row["outgoing_offer_number"]),
                )

                connection.commit()

            except Exception as e:
                connection.rollback()
                print(f"Error updating {row['outgoing_offer_number']}: {str(e)}")

    except Exception as e:
        print(f"Database connection error: {str(e)}")
        raise
    finally:
        if connection:
            connection.close()


if __name__ == "__main__":
    df = pd.read_excel('/Users/arsenijkarpov/Downloads/Подбор квартир (2).xlsx')
    insert_data_to_offer(df)
