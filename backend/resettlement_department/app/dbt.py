import psycopg2
from psycopg2.extras import execute_values, Json
import multiprocessing
import json
from functools import partial
from tqdm import tqdm
import time
from repository.database import get_db_connection as get_db_connection

def get_total_count():
    """Получаем общее количество записей для прогресс-бара"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT COUNT(*) FROM offer")
        return cur.fetchone()[0]
    conn.close()

def get_mapping_dict():
    """Получаем соответствие rsm_apart_id -> new_apart_id"""
    conn = get_db_connection()
    with conn.cursor() as cur:
        cur.execute("SELECT rsm_apart_id::text, new_apart_id::text FROM new_apart")
        return dict(cur.fetchall())
    conn.close()

def process_offer(offer_row, mapping):
    """Обрабатываем одну запись offer"""
    offer_id, old_data = offer_row
    try:
        # Если данные уже в виде dict (а не JSON строка)
        if isinstance(old_data, dict):
            data = old_data
        else:
            data = json.loads(old_data)
        
        updated_data = {}
        
        for rsm_id, value in data.items():
            new_id = mapping.get(rsm_id, rsm_id)
            updated_data[new_id] = value
        
        return (offer_id, Json(updated_data))  # Используем psycopg2.extras.Json
    except Exception as e:
        print(f"\nError processing offer {offer_id}: {e}")
        return None

def update_batch(batch, conn_info):
    """Обновляем пачку записей в БД с использованием execute_values"""
    conn = psycopg2.connect(**conn_info)
    with conn.cursor() as cur:
        # Формируем список кортежей для execute_values
        data_tuples = [(data, offer_id) for offer_id, data in batch]
        
        query = """
            UPDATE offer 
            SET new_aparts = data.new_aparts
            FROM (VALUES %s) AS data (new_aparts, offer_id)
            WHERE offer.offer_id = data.offer_id
        """
        execute_values(
            cur, 
            query, 
            data_tuples,
            template="(%s::jsonb, %s)",
            page_size=1000
        )
    conn.commit()
    conn.close()

def main():
    print("Starting ID mapping update...")
    start_time = time.time()
    
    total_rows = get_total_count()
    print(f"Total offers to process: {total_rows}")
    
    mapping = get_mapping_dict()
    print(f"Loaded {len(mapping)} ID mappings")
    
    conn = get_db_connection()
    conn_info = {
        'dbname': conn.info.dbname,
        'user': conn.info.user,
        'password': conn.info.password,
        'host': conn.info.host,
        'port': conn.info.port
    }
    
    try:
        with conn.cursor(name="offer_cursor") as cur:
            cur.itersize = 5000
            cur.execute("SELECT offer_id, new_aparts FROM offer")
            
            with multiprocessing.Pool(processes=multiprocessing.cpu_count()) as pool:
                processor = partial(process_offer, mapping=mapping)
                batch_size = 2000
                batch = []
                
                with tqdm(total=total_rows, desc="Processing offers") as pbar:
                    for result in pool.imap(processor, cur, chunksize=100):
                        if result:
                            batch.append(result)
                            if len(batch) >= batch_size:
                                update_batch(batch, conn_info)
                                batch = []
                        pbar.update(1)
                    
                    if batch:
                        update_batch(batch, conn_info)
    
    finally:
        conn.close()
    
    total_time = time.time() - start_time
    print(f"\nUpdate completed successfully in {total_time:.2f} seconds")
    print(f"Processing speed: {total_rows/total_time:.2f} offers/second")

if __name__ == "__main__":
    multiprocessing.set_start_method('spawn')
    main()