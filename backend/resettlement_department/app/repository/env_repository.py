from sqlalchemy import text

class EnvRepository:
    def __init__(self, session_maker):
        self.db = session_maker

    async def get_env_history(self):
        async with self.db() as session:
            result = await session.execute(
                text(
                    "SELECT id, name, (updated_at)::varchar, success FROM env.data_updates"
                )
            )
            return result.fetchall()