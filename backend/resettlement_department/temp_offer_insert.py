import pandas as pd
from tqdm import tqdm
import psycopg2
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

def insert_single_offer(cursor, row):
    """Вставляет одну строку данных"""
    try:
        cursor.execute(
            """
            INSERT INTO offer (affair_id, new_aparts, outcoming_date, outgoing_offer_number)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT DO NOTHING
            """,
            (row['affair_id'], row['new_aparts'], row['outcoming_date'], row['outgoing_offer_number'])
        )
        return 1
    except Exception as e:
        print(f"Ошибка при вставке строки: {str(e)}")
        return 0

def process_offers_data(input_file):
    """Основной процесс обработки данных (построчная вставка)"""
    conn = None
    try:
        # 1. Загрузка данных
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
        
        # 3. Построчная обработка
        conn = get_db_connection()
        cursor = conn.cursor()
        
        total_inserted = 0
        with tqdm(total=len(records), desc="Вставка данных") as pbar:
            for row in records:
                inserted = insert_single_offer(cursor, row)
                conn.commit()  # Коммитим после каждой строки
                total_inserted += inserted
                pbar.update(1)
        
        print(f"\nУспешно вставлено {total_inserted} записей из {len(records)}")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
    finally:
        if conn:
            conn.close()

if __name__ == "__main__":
    input_file = 'processed_offers.xlsx'
    process_offers_data(input_file)