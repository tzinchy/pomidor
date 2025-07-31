from pydantic import BaseModel, Field
from datetime import datetime

class MailIndexBase(BaseModel):
    """Базовая модель почтового индекса"""
    mail_index_id: int = Field(..., description="Уникальный идентификатор записи")
    mail_index: int = Field(..., description="Почтовый индекс")
    house_address: str = Field(..., description="Полный адрес дома")


class MailIndexCreate(BaseModel):
    """Модель для создания новой записи"""
    mail_index: int
    house_address: str

class MailIndexUpdate(MailIndexBase):
    """Модель для обновления записи"""
    pass

class MailIndexTable(MailIndexBase):
    """Полная модель записи из таблицы"""
    created_at: datetime = Field(..., description="Дата создания записи")
    updated_at: datetime = Field(..., description="Дата последнего обновления")

    class Config:
        from_attributes = True  # Для совместимости с ORM