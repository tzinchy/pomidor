from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func

from models.base import Base

class Service(Base):
    __tablename__ = 'service'
    __table_args__ = {'schema': 'auth'}
    
    service_id = Column(Integer, primary_key=True, autoincrement=True)
    service = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
