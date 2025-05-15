from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base 

class Division(Base):
    __tablename__ = 'division'
    __table_args__ = {'schema': 'auth'}
    
    division_id = Column(Integer, primary_key=True, autoincrement=True)
    division = Column(String, nullable=False)
    management_id = Column(Integer, ForeignKey('auth.management.management_id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    district_group_id = Column(Integer, ForeignKey('auth.district_group.district_group_id'))