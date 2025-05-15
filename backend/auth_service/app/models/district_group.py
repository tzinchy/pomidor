from sqlalchemy import Column, Integer, DateTime, func, Text, ARRAY
from models.base import Base

class DistrictGroup(Base):
    __tablename__ = 'district_group'
    __table_args__ = {'schema': 'auth'}
    
    district_group_id = Column(Integer, primary_key=True, autoincrement=True)
    description = Column(Text)
    districts_ids = Column(ARRAY(Integer))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    


