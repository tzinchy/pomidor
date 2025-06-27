from sqlalchemy import Column, Integer, String, Date, DateTime, SmallInteger
from sqlalchemy.sql import func
from models.base import Base


class Cin(Base):
    __tablename__ = "cin"

    cin_id = Column(Integer, primary_key=True, autoincrement=True)
    unom = Column(String, unique=True)
    old_address = Column(String)
    cin_address = Column(String)
    cin_schedule = Column(String)
    dep_schedule = Column(String)
    phone_osmotr = Column(String)
    otdel = Column(String)
    start_date = Column(Date)
    phone_otvet = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True))
    manual_load_id = Column(SmallInteger)

    def __repr__(self):
        return f"<Cin(unom='{self.unom}', cin_address='{self.cin_address}')>"
