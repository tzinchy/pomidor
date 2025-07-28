from repository.env_repository import EnvRepository


class EnvService:
    def __init__(self, repository: EnvRepository):
        self.repository = repository

    async def get_env_history(self):
        res = await self.repository.get_env_history()
        return res