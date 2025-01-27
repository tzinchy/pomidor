from database import project_managment_session
from sqlalchemy import text

class HistoryRepository: 
    def __init__(self, db : project_managment_session):
        self.db = db 
    
    async def get_history(self):
        async with self.db as session: 
            res = await session.execute('SELECT * FROM history')
            return res

