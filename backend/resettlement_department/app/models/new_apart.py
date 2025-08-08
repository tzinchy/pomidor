from sqlalchemy import (
    Column,
    Integer,
    String,
    Numeric,
    Boolean,
    DateTime,
    BigInteger,
    text,
)

from models.base import Base


class NewApart(Base):
    __tablename__ = "new_apart"

    rsm_apart_id = Column(BigInteger)
    municipal_district = Column(String)
    house_address = Column(String)
    apart_number = Column(Integer)
    floor = Column(Integer)
    room_count = Column(Integer)
    full_living_area = Column(Numeric(10, 2))
    living_area = Column(Numeric(10, 2))
    rank = Column(Integer)
    history_id = Column(Integer)
    notes = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))
    unom = Column(Integer)
    total_living_area = Column(Numeric(10, 2))
    type_of_settlement = Column(String)
    apart_resource = Column(String)
    un_kv = Column(Integer)
    owner = Column(String)
    street_address = Column(String)
    house_number = Column(Integer)
    house_index = Column(String)
    bulding_body_number = Column(String)
    up_id = Column(BigInteger, unique=True)
    object_id = Column(BigInteger, default=0)
    for_special_needs_marker = Column(Integer, default=0)
    apart_type = Column(String)
    cad_num = Column(String)
    new_apart_id = Column(BigInteger, primary_key=True)
    manual_load_id = Column(Integer)
    is_use = Column(Boolean, default=False)
    is_private = Column(Boolean)
    rsm_notes = Column(String)
    entrance_number = Column(Integer)
    status_id = Column(Integer, default=11)
    area_id = Column(Integer)
    order_id = Column(Integer)
    district_id = Column(Integer)
    district = Column(String(200))
