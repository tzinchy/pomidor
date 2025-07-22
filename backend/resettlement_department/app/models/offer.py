from sqlalchemy import Column, Integer, String, Date, DateTime, BigInteger, text
from sqlalchemy.dialects.postgresql import JSONB
from models.base import Base


class Offer(Base):
    __tablename__ = "offer"

    offer_id = Column(Integer, primary_key=True, autoincrement=True)
    status_id = Column(Integer)
    notes = Column(String)
    user_id = Column(Integer)
    sentence_date = Column(DateTime(timezone=True))
    give_date = Column(DateTime(timezone=True))
    answer_date = Column(DateTime(timezone=True))
    sentence_number = Column(Integer)
    selection_action = Column(String)
    conditions = Column(String)
    claim = Column(String)
    subject_id = Column(Integer)
    object_id = Column(Integer)
    updated_at = Column(DateTime(timezone=True), server_default=text("now()"))
    affair_id = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=text("now()"))
    new_aparts = Column(JSONB)
    outgoing_offer_number = Column(Integer)
    offer_date = Column(Date)
    order_id = Column(BigInteger)
    outcoming_date = Column(Date)
