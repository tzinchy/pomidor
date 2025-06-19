from repository.history_repository import HistoryRepository
import os
import glob


class HistoryService:
    def __init__(self, repository: HistoryRepository):
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

    async def cancell_manual_load(self, manual_load_id):
        res = await self.repository.cancell_manual_load(manual_load_id)
        return res

    async def get_manual_load_history(self):
        res = await self.repository.get_manual_load_history()
        return res
    
    def clear_matching_files(self):
        try:
            files = glob.glob('programs/pomidor/backend/resettlement_department/app/uploads/*.xlsx')
            for f in files:
                try:
                    if os.path.isfile(f):
                        os.remove(f)
                        print(f"Удален файл: {f}")  
                    else:
                        print(f"Файл не найден: {f}")
                except Exception as e:
                    print(f"Ошибка при удалении файла {f}: {e}")
        except Exception as e:
            print(f"Ошибка при поиске файлов: {e}")

