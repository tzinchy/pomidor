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

    async def cancellmatching(self, history_id : int):
        async with self.db() as session:
            try:
                query = read_sql_query(f'{RECOMMENDATION_FILE_PATH}/CancellMatching.sql')
                result = await session.execute(text(query), {'history_id' : history_id})
                await session.commit()
                if result.fetchone()[0] == 'done':
                    return 200
            except Exception: 
                raise Exception
            
    
