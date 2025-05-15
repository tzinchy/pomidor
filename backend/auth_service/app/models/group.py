from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from models.base import Base 

class Group(Base):
    __tablename__ = 'group'
    __table_args__ = {'schema': 'auth'}
    
    group_id = Column(Integer, primary_key=True, autoincrement=True)
    group = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    service_table_id = Column(Integer, ForeignKey('auth.service_table.service_table_id'))
    actions = Column(ARRAY(Integer))