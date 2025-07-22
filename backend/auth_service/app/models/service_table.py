from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base 

class ServiceTable(Base):
    __tablename__ = 'service_table'
    __table_args__ = {'schema': 'auth'}
    
    service_table_id = Column(Integer, primary_key=True, autoincrement=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    service_id = Column(Integer, ForeignKey('auth.service.service_id'))
    service_table = Column(String, nullable=False)