from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Status(Base):
    __tablename__ = 'status'
    
    status_id = Column(Integer, primary_key=True)
    status = Column(String)
    
    def __repr__(self):
        return f"<Status(id={self.status_id}, name='{self.status}')>"