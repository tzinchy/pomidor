from sqlalchemy import Column, Integer, String
from models.base import Base


class Status(Base):
    __tablename__ = "status"

    status_id = Column(Integer, primary_key=True, autoincrement=True)
    status = Column(String)
