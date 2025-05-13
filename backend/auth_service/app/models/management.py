from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base 


class Management(Base):
    __tablename__ = 'management'
    __table_args__ = {'schema': 'auth'}
    
    management_id = Column(Integer, primary_key=True, autoincrement=True)
    management = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    department_id = Column(Integer, ForeignKey('auth.department.department_id'))