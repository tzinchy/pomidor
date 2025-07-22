from sqlalchemy import (
    Column,
    Integer,
    String,
    Date,
    DateTime,
    BigInteger,
    text,
    Numeric,
    Boolean,
)
from models.base import Base


class OldApart(Base):
    __tablename__ = "old_apart"

    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))
    affair_id = Column(BigInteger, primary_key=True)
    kpu_number = Column(String)
    fio = Column(String)
    surname = Column(String)
    firstname = Column(String)
    lastname = Column(String)
    people_in_family = Column(Integer)
    category = Column(Integer)
    cad_num = Column(String(200))
    notes = Column(String)
    house_address = Column(String)
    apart_number = Column(String(50))
    room_count = Column(Integer)
    floor = Column(Integer)
    living_area = Column(Numeric(10, 2))
    people_v_dele = Column(Integer)
    people_uchet = Column(Integer)
    apart_type = Column(String)
    manipulation_notes = Column(String)
    municipal_district = Column(String)
    is_special_needs_marker = Column(Integer, default=0)
    min_floor = Column(Integer, default=0)
    max_floor = Column(Integer, default=0)
    buying_date = Column(Date)
    is_queue = Column(Integer, default=0)
    queue_square = Column(Numeric(10, 2), default=0)
    type_of_settlement = Column(String(120), default="Н/А")
    history_id = Column(Integer)
    rank = Column(Integer)
    kpu_another = Column(String)
    rsm_status = Column(String)
    is_hand_download = Column(Integer)
    unom = Column(String)
    manual_load_id = Column(Integer)
    is_use = Column(Boolean)
    rsm_notes = Column(String)
    status_id = Column(Integer, default=8)
    total_living_area = Column(Numeric(10, 2))
    full_living_area = Column(Numeric(10, 2))
    was_queue = Column(Integer, default=0)
    removal_reason = Column(String)
    removal_date = Column(String)
    rsm_another_closed = Column(String)
    is_hidden = Column(Boolean, default=False)
    district_id = Column(Integer)
    district = Column(String(200))
