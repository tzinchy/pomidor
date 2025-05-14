from sqlalchemy.ext.asyncio import AsyncSession

class AdminRepository: 
    def __init__(self, db : AsyncSession):
        self.db = db
    '''
    def get_groups(self):
        async with self.db() as session: 
            pass 
       ''' 