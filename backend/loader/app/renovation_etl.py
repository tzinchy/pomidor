import time
import json
from tqdm import tqdm
from psycopg2.extras import Json
from repository.database import get_connection, get_source_connection
from core.config import tables

def executor(table: str, table_params: str):
    try:
        start_time = time.time()
        schema, table_name = table.split('.')
        
        # 1. Получаем данные из источника с информацией о типах столбцов
        with get_source_connection() as source_connection:
            source_connection.autocommit = False
            
            with source_connection.cursor() as regular_cursor:
                # Get column metadata
                regular_cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table_name}' 
                    AND table_schema = '{schema}'
                """)
                column_types = {row[0]: row[1] for row in regular_cursor.fetchall()}
                
                # Identify JSON columns
                json_columns = [col for col, dtype in column_types.items() 
                               if dtype in ('json', 'jsonb')]
                
                # Get total rows count
                regular_cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total_rows = regular_cursor.fetchone()[0]
                
                if total_rows == 0:
                    print(f"\n{table}: Нет данных для переноса")
                    return
                
                print(f"\n{table}: Начинаем перенос {total_rows:,} строк")
            
            source_connection.commit()
            
            with source_connection.cursor(name='server_side_cursor') as cursor:
                cursor.itersize = 10000
                cursor.execute(f'SELECT {table_params} FROM {table}')
                
                # 2. Вставляем данные в целевую БД
                with get_connection() as target_connection:
                    target_connection.autocommit = False
                    
                    with target_connection.cursor() as target_cursor:
                        # Подготовка запроса
                        columns = table_params.split(', ')
                        placeholders = ', '.join(['%s'] * len(columns))
                        updates = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])
                        
                        insert_query = f"""
                            INSERT INTO {table} ({table_params}) 
                            VALUES ({placeholders})
                            ON CONFLICT (id) DO UPDATE SET {updates}
                        """
                        
                        # Временное отключение индексов для больших таблиц
                        if total_rows > 100000:
                            target_cursor.execute(f"ALTER TABLE {table} DISABLE TRIGGER ALL;")
                        
                        # Чтение и вставка с прогресс-баром
                        inserted = 0
                        with tqdm(total=total_rows, desc="Перенос") as pbar:
                            while True:
                                batch = cursor.fetchmany(5000)
                                if not batch:
                                    break
                                
                                # Обработка JSON данных для всего пакета
                                processed_batch = []
                                for row in batch:
                                    processed_row = list(row)  # Преобразуем в список для изменения
                                    for i, col_name in enumerate(columns):
                                        if col_name in json_columns and processed_row[i] is not None:
                                            processed_row[i] = Json(processed_row[i])
                                    processed_batch.append(tuple(processed_row))
                                
                                target_cursor.executemany(insert_query, processed_batch)
                                inserted += len(processed_batch)
                                pbar.update(len(processed_batch))
                                
                                # Периодический коммит
                                if inserted % 50000 == 0:
                                    target_connection.commit()
                        
                        # Восстановление индексов
                        if total_rows > 100000:
                            target_cursor.execute(f"ALTER TABLE {table} ENABLE TRIGGER ALL;")
                            target_cursor.execute(f"REINDEX TABLE {table};")
                        
                        target_connection.commit()
                        
                        elapsed = time.time() - start_time
                        print(f"Успешно: {inserted:,} строк | Скорость: {inserted/elapsed:.1f} строк/сек")
            
            source_connection.commit()
                        
    except Exception as e:
        print(f"\n[ОШИБКА] {table}: {str(e)}")
        if 'target_connection' in locals():
            target_connection.rollback()
        if 'source_connection' in locals():
            source_connection.rollback()
        raise

# Основной цикл обработки таблиц
if __name__ == "__main__":
    total_tables = len(tables)
    print(f"Начинаем миграцию {total_tables} таблиц...")
    
    
    # Обработка таблиц с прогресс-баром
    for i, (table, params) in enumerate(tqdm(tables.items()), 1):
        print(f"\n[{i}/{total_tables}] Обработка таблицы: {table}")
        executor(table, ', '.join(params))
    
    print("\nМиграция завершена!")