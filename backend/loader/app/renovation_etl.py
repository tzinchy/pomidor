from core.config import tables
from repository.database import get_connection, get_source_connection

def executor(table: str, table_params: str):
    try:
        # Get data from source
        with get_source_connection() as source_connection:
            with source_connection.cursor() as cursor: 
                cursor.execute(f'SELECT {table_params} FROM {table}')
                source_data = cursor.fetchall()
                
        if not source_data:
            print(f'No data found for table: {table}')
            return
            
        # Prepare the INSERT statement with ON CONFLICT (UPSERT)
        columns = table_params.split(', ')
        placeholders = ', '.join(['%s'] * len(columns))
        updates = ', '.join([f"{col} = EXCLUDED.{col}" for col in columns if col != 'id'])
        
        insert_query = f"""
            INSERT INTO {table} ({table_params}) 
            VALUES ({placeholders})
            ON CONFLICT (id) DO UPDATE SET {updates}
        """
        
        # Insert data into target
        with get_connection() as connection: 
            with connection.cursor() as cursor:
                cursor.executemany(insert_query, source_data)
                connection.commit()
                print(f'Successfully migrated {len(source_data)} rows to {table}')
                
    except Exception as e: 
        print(f'Error migrating table {table}: {str(e)}')
        # Consider adding logging or re-raising the exception if needed

# Process all tables
for table, table_params in tables.items(): 
    executor(table, ', '.join(table_params))