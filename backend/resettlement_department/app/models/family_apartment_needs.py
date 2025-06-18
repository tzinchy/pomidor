from sqlalchemy import Column, Integer, Boolean, DateTime, ForeignKey, String
from sqlalchemy.sql import func
from models.base import Base
from models.status import Status
from models.family_structure import FamilyStructure
from models.history import History
from sqlalchemy.orm import relationship


class FamilyApartmentNeeds(Base):
    __tablename__ = "family_apartment_needs"

    family_apartment_needs_id = Column(Integer, primary_key=True)
    status_id = Column(Integer, ForeignKey("status.status_id"))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
    affair_id = Column(Integer, ForeignKey("family_structure.affair_id"))
    up_id = Column(Integer, unique=True)
    rank = Column(Integer)
    history_id = Column(Integer, ForeignKey("history.history_id"))
    kpu_num = Column(String)
    is_use = Column(Boolean, default=False)

    status = relationship("Status")
    family_structure = relationship("FamilyStructure")
    history = relationship("History")
