from sqlalchemy import Column, Integer, String, Numeric, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base
from models.history import History
from sqlalchemy.orm import relationship

class NewApart(Base):
    __tablename__ = 'new_apart'
    
    new_apart_id = Column(Integer, primary_key=True)
    district = Column(String)
    municipal_district = Column(String)
    house_address = Column(String)
    apart_number = Column(int)
    floor = Column(Integer)
    room_count = Column(Integer)
    full_living_area = Column(Numeric(10, 2))
    living_area = Column(Numeric(10, 2))
    rank = Column(Integer)
    history_id = Column(Integer, ForeignKey('history.history_id'))
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    building_id = Column(Integer)
    total_living_area = Column(Numeric(10, 2))
    type_of_settlement = Column(String)
    apart_resource = Column(String)
    un_kv = Column(Integer)
    owner = Column(String)
    status = Column(String)
    apart_kad_number = Column(String)
    room_kad_number = Column(String)
    street_address = Column(String)
    house_number = Column(Integer)
    house_index = Column(String)
    bulding_body_number = Column(String)
    up_id = Column(Integer, unique=True)
    object_id = Column(Integer)
    for_special_needs_marker = Column(Integer, default=0)

    history = relationship("History")