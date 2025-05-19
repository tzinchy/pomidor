from models.user import User

class AdminService:
    def __init__(self, repository):
        self.repository = repository

    async def create_user(
        self,
        **user_config
    ) -> None:
        async with self.db() as session:
            await session.add(User(**user_config))

    async def get_groups(self): 
        async with self.repository.
