from repository.history_repository import HistoryRepository

class HistoryService: 
    def __init__(self, repository : HistoryRepository):
        self.repository = repository
    
    async def get_history(self):
        res = await self.repository.get_history()
        return res
    
    async def cancell_history(self, history_id):
        res = await self.repository.cancell_history(history_id)
        return res
    
    async def approve_history(self, history_id):
        res = await self.repository.approve_history(history_id)
        return res