from sqlalchemy import Column, Integer, String, Numeric, DateTime, JSON
from sqlalchemy.sql import func
from models.base import Base

class FamilyStructure(Base):
    __tablename__ = 'family_structure'
    
    affair_id = Column(Integer, primary_key=True)
    kpu_number = Column(String)
    fio = Column(String(100))
    surname = Column(String(100))
    firstname = Column(String(100))
    lastname = Column(String(100))
    people_in_family = Column(Integer)
    category = Column(Integer)
    cad_num = Column(String(200))
    notes = Column(String)
    documents = Column(JSON)
    district = Column(String(200))
    house_address = Column(String)
    apart_number = Column(String(50))
    room_count = Column(Integer)
    floor = Column(Integer)
    full_living_area = Column(Numeric)
    living_area = Column(Numeric)
    people_v_dele = Column(Integer)
    people_uchet = Column(Integer)
    total_living_area = Column(Numeric)
    apart_type = Column(String)
    manipulation_notes = Column(String)
    municipal_district = Column(String)
    is_special_needs_marker = Column(Integer, default=0)
    min_floor = Column(Integer, default=0)
    max_floor = Column(Integer, default=0)
    buying_date = Column(DateTime)
    is_queue = Column(Integer)
    queue_square = Column(Numeric(10, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


