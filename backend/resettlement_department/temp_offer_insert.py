import pandas as pd
from tqdm import tqdm
import psycopg2
from psycopg2.extras import execute_values
from app.core.config import settings

def get_db_connection():
    """Создает соединение с БД"""
    return psycopg2.connect(
        host=settings.project_management_setting.DB_HOST,
        user=settings.project_management_setting.DB_USER,
        password=settings.project_management_setting.DB_PASSWORD,
        port=settings.project_management_setting.DB_PORT,
        database=settings.project_management_setting.DB_NAME,
    )

def insert_offers_batch(cursor, batch):
    """Вставляет одну пачку данных"""
    try:
        # Преобразуем данные в список кортежей
        data_tuples = [
            (row['affair_id'], row['new_aparts'], row['outcoming_date'], row['outgoing_offer_number'])
            for row in batch
        ]
        
        # Используем execute_values для быстрой вставки
        execute_values(
            cursor,
            """
            INSERT INTO offer (affair_id, new_aparts, outcoming_date, outgoing_offer_number)
            VALUES %s
            ON CONFLICT DO NOTHING
            """,
            data_tuples,
            page_size=len(batch))
        return len(batch)
    except Exception as e:
        print(f"Ошибка при вставке пачки: {str(e)}")
        return 0

def process_offers_data(input_file):
    """Основной процесс обработки данных (последовательная версия)"""
    conn = None
    try:
        # 1. Загрузка данных с оптимизацией
        offers_df = pd.read_excel(
            input_file,
            usecols=['affair_id', 'new_aparts', 'outcoming_date', 'outgoing_offer_number'],
            dtype={
                'affair_id': 'int32',
                'new_aparts': 'str',
                'outgoing_offer_number': 'str'
            }
        )
        
        # 2. Подготовка данных
        offers_df = offers_df.where(pd.notnull(offers_df), None)
        records = offers_df.to_dict('records')
        
        # 3. Настройка батчинга
        batch_size = 10000  # Можно увеличить, так как работаем последовательно
        batches = [records[i:i + batch_size] for i in range(0, len(records), batch_size)]
        
        # 4. Последовательная обработка
        conn = get_db_connection()
        cursor = conn.cursor()
        
        total_inserted = 0
        with tqdm(total=len(records), desc="Вставка данных") as pbar:
            for batch in batches:
                inserted = insert_offers_batch(cursor, batch)
                conn.commit()
                total_inserted += inserted
                pbar.update(len(batch))
        
        print(f"\nУспешно вставлено {total_inserted} записей из {len(records)}")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    input_file = 'processed_offers.xlsx'
    process_offers_data(input_file)