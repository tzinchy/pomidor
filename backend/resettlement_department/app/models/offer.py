from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.sql import func
from models.base import Base
from models.status import Status
from models.new_apart import NewApart
from models.family_apartment_needs import FamilyApartmentNeeds
from sqlalchemy.orm import relationship

class Offer(Base):
    __tablename__ = 'offer'
    
    offer_id = Column(Integer, primary_key=True)
    status_id = Column(Integer, ForeignKey('status.status_id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    notes = Column(String)
    user_id = Column(Integer)
    sentence_date = Column(DateTime)
    give_date = Column(DateTime)
    answer_date = Column(DateTime)
    sentence_number = Column(Integer)
    selection_action = Column(String)
    conditions = Column(String)
    claim = Column(String)
    subject_id = Column(Integer)
    object_id = Column(Integer)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    new_apart_id = Column(Integer, ForeignKey('new_apart.new_apart_id'))
    family_apartment_needs_id = Column(Integer, ForeignKey('family_apartment_needs.family_apartment_needs_id'), unique=True)

    status = relationship("Status")
    new_apart = relationship("NewApart")
    family_apartment_needs = relationship("FamilyApartmentNeeds")