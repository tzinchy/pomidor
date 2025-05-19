from sqlalchemy import Column, Integer, String, DateTime, func
from models.base import Base

class Department(Base):
    __tablename__ = 'department'
    __table_args__ = {'schema': 'auth'}
    
    department_id = Column(Integer, primary_key=True, autoincrement=True)
    department = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())