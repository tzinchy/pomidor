import time
import json
from decimal import Decimal
from datetime import date, datetime
from tqdm import tqdm
from psycopg2 import extras
from psycopg2.extras import Json
from core.config import tables
from repository.database import get_connection, get_source_connection


def clean_value(value):
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, str):
        return value.replace('\t', ' ').replace('\n', ' ').strip()
    return value


def executor(table: str, columns: list):
    start_time = time.time()
    print(f"{table}: Начинаем загрузку")

    with get_source_connection() as source_conn, get_connection() as target_conn:
        with source_conn.cursor() as source_cur, target_conn.cursor() as target_cur:
            # Определим индексы json/jsonb полей
            schema, table_name = table.split(".")
            source_cur.execute("""
                SELECT column_name, data_type
                FROM information_schema.columns
                WHERE table_schema = %s AND table_name = %s
            """, (schema, table_name))
            col_type_map = {row[0]: row[1] for row in source_cur.fetchall()}
            json_indexes = [
                idx for idx, col in enumerate(columns)
                if col_type_map.get(col) in ("json", "jsonb")
            ]

            # Забираем данные
            source_cur.execute(f"SELECT {', '.join(columns)} FROM {table}")
            rows = source_cur.fetchall()

            if not rows:
                print(f"{table}: Нет данных для вставки")
                return

            # Чистим и оборачиваем JSON
            cleaned_rows = []
            for row in rows:
                cleaned_row = []
                for i, value in enumerate(row):
                    cleaned = clean_value(value)
                    if i in json_indexes and cleaned is not None:
                        try:
                            if isinstance(cleaned, str):
                                cleaned = json.loads(cleaned)
                            cleaned = Json(cleaned)
                        except Exception:
                            cleaned = Json({})
                    cleaned_row.append(cleaned)
                cleaned_rows.append(tuple(cleaned_row))

            # Запрос INSERT
            insert_query = f"""
                INSERT INTO {table} ({', '.join(columns)})
                VALUES %s
                ON CONFLICT (id) DO UPDATE SET
                {', '.join(f"{col} = EXCLUDED.{col}" for col in columns if col != 'id')}
            """

            extras.execute_values(target_cur, insert_query, cleaned_rows)
            target_conn.commit()

            elapsed = time.time() - start_time
            print(f"✅ {table}: {len(rows):,} строк вставлено | {elapsed:.2f} сек | Скорость: {len(rows)/elapsed:.1f} строк/сек")


if __name__ == "__main__":
    print("📤 SELECT и вставка из source (dashboard) в point (project)...")
    for table, columns in tqdm(tables.items(), desc="PostgreSQL перенос"):
        executor(table, columns)

    print("\n✅ Перенос завершён")
