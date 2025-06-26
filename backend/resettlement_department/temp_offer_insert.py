import pandas as pd
from tqdm import tqdm
import psycopg2
import json
from datetime import datetime
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


def process_offers_data(input_file):
    """Основной процесс обработки данных"""
    conn = None
    try:
        # 1. Загрузка данных
        df = pd.read_excel(
            input_file,
            usecols=['offer_id', 'affair_id', 'new_aparts', 'outcoming_date', 'outgoing_offer_number'],
            dtype={
                'affair_id': 'int32',
                'outgoing_offer_number': 'str'
            }
        )
        df = df.sort_values('offer_id')
        # 2. Подготовка данных
        df = df.where(pd.notnull(df), None)
        
        # 3. Обработка данных
        conn = get_db_connection()
        cursor = conn.cursor()
        
        total = 0
        with tqdm(total=len(df), desc="Обработка офферов") as pbar:
            for _, row in df.iterrows():
                new_aparts = json.loads(row['new_aparts']) if isinstance(row['new_aparts'], str) else row['new_aparts']

                # Вставляем запись
                cursor.execute("""
                    INSERT INTO offer (
                        offer_id,affair_id, new_aparts, outcoming_date, outgoing_offer_number
                    ) VALUES (%s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                    RETURNING offer_id
                    """, (
                        row['offer_id'],
                        row['affair_id'],
                        json.dumps(new_aparts),
                        row['outcoming_date'],
                        row['outgoing_offer_number']
                    ))
                
                conn.commit() 
                pbar.update(1)
        
        print(f"\nУспешно обработано {total} из {len(df)} записей")
        
    except Exception as e:
        print(f"Критическая ошибка: {str(e)}")
        if conn: conn.rollback()
    finally:
        if conn: conn.close()


if __name__ == "__main__":
    # Исправляем существующие данные
    
    # Обрабатываем новые данные
    input_file = 'processed_offers.xlsx'
    process_offers_data(input_file)