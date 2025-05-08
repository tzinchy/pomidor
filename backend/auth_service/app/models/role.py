from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base 

class Role(Base):
    __tablename__ = 'role'
    __table_args__ = {'schema': 'auth'}
    
    role_id = Column(Integer, primary_key=True)
    service_id = Column(Integer, ForeignKey('auth.service.service_id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    role = Column(String, unique=True)