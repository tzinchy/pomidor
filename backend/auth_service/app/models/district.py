from sqlalchemy import Column, Integer, String, DateTime, func
from models.base import Base

class District(Base):
    __tablename__ = 'district'
    __table_args__ = {'schema': 'auth'}
    
    district_id = Column(Integer, primary_key=True, autoincrement=True)
    district = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
