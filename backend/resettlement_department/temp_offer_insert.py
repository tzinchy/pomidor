import json

import numpy as np
import pandas as pd
import psycopg2
from tqdm import tqdm
from psycopg2 import errors

from app.core.config import settings


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
        columns_offer_name = {
            "ID": "offer_id",
            "Идентификатор дела": "affair_id",
            "Идентификатор площади": "new_apart_id",
            "Исх. № предложения": "outgoing_offer_number",
            "Дата предложения": "offer_date",
        }
        columns_db = ["affair_id", "new_aparts", "outgoing_offer_number", "offer_date"]
        columns_decline_name = {
            "Претензия": "notes",
        }
        columns_decline_db = list(columns_decline_name.values())
        df.rename(columns=columns_offer_name, inplace=True)
        df.rename(columns=columns_decline_name, inplace=True)

        df["affair_id"] = pd.to_numeric(df["affair_id"], errors="coerce")

        # Преобразование типов
        df["offer_date"] = df["offer_date"].astype(str)
        df["affair_id"] = df["affair_id"].astype("Int64")
        df["offer_id"] = df["offer_id"].astype("Int64")
        df["new_apart_id"] = df["new_apart_id"].astype("Int64")
        df = df.dropna(subset=["offer_id", "affair_id", "new_apart_id"])
        df = df.replace({np.nan: None, "00:00:00": None})
        # Убрать combine_new_apart_id_and_decline_reason_id???
        # df["new_aparts"] = df.apply(combine_new_apart_id_and_decline_reason_id, axis=1)

        df.drop_duplicates("offer_id", inplace=True)
        df.sort_values("offer_id", inplace=True)

        connection = psycopg2.connect(
            host=settings.project_management_setting.DB_HOST,
            user=settings.project_management_setting.DB_USER,
            password=settings.project_management_setting.DB_PASSWORD,
            port=settings.project_management_setting.DB_PORT,
            database=settings.project_management_setting.DB_NAME,
        )

        # with connection:
        #     with connection.cursor() as cursor:
        #         with open("repeated.txt", "w") as f:
        #             for affair_id in tqdm(df["affair_id"]):
        #                 cursor.execute(f"""
        #                                 SELECT 1 FROM old_apart WHERE affair_id = {affair_id}
        #                                 """)
        #                 if not cursor.fetchone():
        #                     f.write(str(affair_id) + "\n")
        # return


        # args = []
        # for _, row in df.iterrows():
        #     # Подготовка значений для вставки
        #     values = []
        #     for col in columns_db:
        #         val = row[col]
        #         if isinstance(val, str):
        #             val = val.replace("'", "''")
        #             values.append(f"'{val}'")
        #         elif val is None:
        #             values.append("NULL")
        #         elif isinstance(val, (dict, list)):
        #             values.append(f"'{json.dumps(val)}'")
        #         else:
        #             values.append(str(val))
        #     args.append("({})".format(", ".join(values)))
        # 
        # args = []
        # for _, row in df.iterrows():
        #     # Подготовка значений для вставки
        #     values = []
        #     for col in columns_db:
        #         val = row[col]
        #         if isinstance(val, str):
        #             val = val.replace("'", "''")
        #             values.append(f"'{val}'")
        #         elif val is None:
        #             values.append("NULL")
        #         elif isinstance(val, (dict, list)):
        #             values.append(f"'{json.dumps(val)}'")
        #         else:
        #             values.append(str(val))
        #     args.append(values)

        # with connection:
        #     with connection.cursor() as cursor:
                # SQL для вставки/обновления
                # create_temp_table = """
                # -- Шаг 1: Создать временную таблицу
                # CREATE TEMP TABLE temp_offers_to_insert (
                #     offer_id INT PRIMARY KEY, -- или какой у вас тип
                #     affair_id INT,
                #     new_aparts JSONB,
                #     created_at TIMESTAMPTZ DEFAULT NOW(),
                #     updated_at TIMESTAMPTZ DEFAULT NOW()
                # );
                # """
                # insert_into_temp_table = f"""
                # -- Шаг 2: Загрузить данные во временную таблицу
                # INSERT INTO temp_offers_to_insert (
                #     {", ".join(columns_db)}
                # ) VALUES {",".join(args)}
                # ON CONFLICT (offer_id) 
                # DO UPDATE SET
                #     {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
                #     updated_at = NOW()
                # """
                # insert_into_offer = """
                # -- Шаг 3: Выполнить основной INSERT ... SELECT с проверкой FK и ON CONFLICT
                # INSERT INTO public.offer (
                #     offer_id, affair_id, new_aparts, created_at, updated_at
                # )
                # SELECT
                #     t.offer_id, t.affair_id, t.new_aparts, t.created_at, t.updated_at
                # FROM
                #     temp_offers_to_insert t
                # LEFT JOIN old_apart o ON t.affair_id = o.affair_id
                # WHERE
                #     o.affair_id IS NOT NULL
                # ON CONFLICT (offer_id)
                # DO UPDATE SET
                #     affair_id = EXCLUDED.affair_id,
                #     new_aparts = EXCLUDED.new_aparts,
                #     updated_at = NOW();
                # """
                # insert_sql = f"""
                #     INSERT INTO public.offer (
                #         {", ".join(columns_db)}
                #     ) VALUES {",".join(args)}
                #     ON CONFLICT (offer_id) 
                #     DO UPDATE SET
                #         {", ".join(f"{col} = EXCLUDED.{col}" for col in columns_db)},
                #         updated_at = NOW()
                # """
                # with open("output.txt", "w") as f:
                #     f.write("\n".join([create_temp_table, insert_into_temp_table, insert_into_offer]))

        df = df.sort_values('offer_id')
        cursor = connection.cursor()
        for _, row in tqdm(df.iterrows(), miniters=50):
            try:
                if row["notes"]:
                    cursor.execute(f"""
                        INSERT INTO public.decline_reason(notes) VALUES ('{row["notes"]}')
                        RETURNING decline_reason_id;
                    """)
                    decline_reason_id = cursor.fetchone()[0]
                    row["new_aparts"] = {str(row["new_apart_id"]): {"status_id": 2, "decline_reason_id": decline_reason_id}}
                else:
                    row["new_aparts"] = {str(row["new_apart_id"]): {"status_id": 7}}
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


if __name__ == "__main__":
    df = pd.read_excel("/Users/macbook/Downloads/Подбор квартир.xlsx")
    insert_data_to_offer(df)