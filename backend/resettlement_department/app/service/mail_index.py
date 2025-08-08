
from repository.mail_index_repository import MailIndexRepositroy
from fastapi import HTTPException, status

class MailIndexService:
    def __init__(self, repository: MailIndexRepositroy):
        self.repository = repository

    async def get_mail_index(self):
        return await self.repository.get_mail_index()
    
    async def update_mail_index(self, mail_index):
        return await self.repository.update_mail_index(mail_index=mail_index)
    
    async def create_mail_index(self, mail_index):
        return await self.repository.create_mail_index(mail_index=mail_index)

