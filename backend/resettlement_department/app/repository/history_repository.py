from sqlalchemy import text
from utils.sql_reader import read_sql_query
from core.config import RECOMMENDATION_FILE_PATH


class HistoryRepository: 
    def __init__(self, session_maker):
        self.db = session_maker

    async def get_history(self):
        async with self.db() as session: 
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/HistoryQuery.sql')
            result = await session.execute(text(query))
            rows = result.fetchall()  # Fetch all rows
            return [row._asdict() for row in rows]  # Convert each row to a dict

    async def cancell_history(self, history_id : int):
        async with self.db() as session:
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/CancellHistory.sql')
            result = await session.execute(text(query), {'history_id' : history_id})
            await session.commit()
            if result.fetchone()[0] == 'done':
                return 'cancell succes'

            
    async def approve_history(self, history_id : int): 
        async with self.db() as session: 
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/UpdateHistoryStatus.sql')
            result = await session.execute(text(query), {'history_id' : history_id})
            await session.commit()
            return 'succes'
        
    async def get_env_history(self):
        async with self.db() as session:
            result = await session.execute(text('SELECT id, name, (updated_at)::varchar, success FROM env.data_updates'))
            return result.fetchall()
    
    async def cancell_manual_load(self, manual_load_id):
        async with self.db() as session:
            query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/CancellManualLoad.sql')
            result = await session.execute(text(query), {'manual_load_id' : manual_load_id})
            await session.commit()
            if result.fetchone()[0] == 'done':
                return 'cancell succes'
        
    async def get_manual_load_history(self):
        async with self.db() as session: 
            result = await session.execute(text('SELECT manual_load_id, filename, file_path, is_old_apart, is_new_apart, is_cin, created_at, updated_at FROM manual_load'))
            rows = result.fetchall() 
            return [row._asdict() for row in rows]  # Convert each row to a dict
