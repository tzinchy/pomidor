from sqlalchemy import Column, Integer, ARRAY, String, DateTime
from sqlalchemy.sql import func
from models.base import Base

class History(Base):
    __tablename__ = 'history'
    
    history_id = Column(Integer, primary_key=True)
    old_house_addresses = Column(ARRAY(String))
    new_house_addresses = Column(ARRAY(String))
    status_id = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())