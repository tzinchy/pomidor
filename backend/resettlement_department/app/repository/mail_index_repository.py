from sqlalchemy import text, select, insert, update
from sqlalchemy.orm import sessionmaker
from core.logger import logger
from models.mail_index import MailIndex
from typing import Optional
from schema.mail_index import MailIndexCreate, MailIndexUpdate


class MailIndexRepositroy:  
    def __init__(self, session_maker: sessionmaker):
        self.db = session_maker

    async def get_mail_index(self):
        try:
            async with self.db() as session:
                query = "SELECT * FROM mail_index"
                
            logger.query(query)
            result = await session.execute(text(query))

            return [dict(row._mapping) for row in result]
        except Exception as e: 
            print(e)

    async def update_mail_index(self, mail_index : MailIndexUpdate):
        async with self.db() as session:
            mail_index_data = mail_index.dict()
            
            if mail_index.mail_index_id:
                stmt = (
                    update(MailIndex)
                    .where(MailIndex.mail_index_id == mail_index.mail_index_id)
                    .values(**mail_index_data)
                    .execution_options(synchronize_session="fetch")
                )
            else:
                stmt = insert(MailIndex).values(**mail_index_data)
            
            await session.execute(stmt)
            await session.commit()

    async def create_mail_index(self, mail_index : MailIndexCreate):
        async with self.db() as session:
            data = mail_index.model_dump()
            stmt = insert(MailIndex).values(**data).returning(MailIndex)
            result = await session.execute(stmt)
            new_cin = result.scalar_one()
            print(new_cin)
            await session.commit()
            return new_cin
                