from models.base import Base
from sqlalchemy import Column, Date, DateTime, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


class MailIndex(Base):
    __tablename__ = "mail_index"

    mail_index_id = Column(Integer, primary_key=True, autoincrement=True)
    mail_index = Column(Integer, nullable=False)
    house_address = Column(String, unique=True, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

