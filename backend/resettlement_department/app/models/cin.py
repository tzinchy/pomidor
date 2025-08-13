from models.base import Base
from sqlalchemy import Column, Date, DateTime, Integer, SmallInteger, String
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func


class Cin(Base):
    __tablename__ = "test_cin"

    cin_id = Column(Integer, primary_key=True, autoincrement=True)
    unom = Column(String, unique=True)
    house_address = Column(String)
    district = Column(String)
    municipal_district = Column(String)
    cin_address = Column(String)
    cin_schedule = Column(String)
    dep_schedule = Column(String)
    phone_osmotr = Column(String)
    otdel = Column(String)
    phone_otvet = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    manual_load_id = Column(SmallInteger)
    start_dates_by_entrence = Column(JSONB)
    full_cin_address = Column(String)
    full_house_address = Column(String)
    otsel_addresses_and_dates = Column(JSONB)
    ispolnitel = Column(String)

    def __repr__(self):
        return f"<Cin(unom='{self.unom}', cin_address='{self.cin_address}')>"
