from sqlalchemy import Column, Integer, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base 


class Position(Base):
    __tablename__ = 'position'
    __table_args__ = {'schema': 'auth'}
    
    position_id = Column(Integer, primary_key=True, autoincrement=True)
    position_list_id = Column(Integer, ForeignKey('auth.position_list.position_list_id'))
    management_id = Column(Integer, ForeignKey('auth.management.management_id'))
    division_id = Column(Integer, ForeignKey('auth.division.division_id'))
    obey_id = Column(Integer)
    position_rank = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
