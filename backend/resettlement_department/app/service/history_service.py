from sqlalchemy import text
from repository.history_repository import HistoryRepository

class HistoryRepository: 
    def __init__(self, history_repository : HistoryRepository):
        self.history_repository = history_repository
    
    async def get_history(self):
        return await self.history_repository.get_history()


