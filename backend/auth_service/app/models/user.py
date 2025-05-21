from sqlalchemy import Column, Integer, String, BigInteger, DateTime, ForeignKey, ARRAY
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from models.base import Base

class User(Base):
    __tablename__ = 'user'
    __table_args__ = {'schema': 'auth'}
    
    user_uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    login = Column(String, unique=True)
    email = Column(String, unique=True)
    password = Column(String)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    telegram_token = Column(String)
    telegram_chat_id = Column(BigInteger)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    roles = Column(ARRAY(Integer))
    district_group_id = Column(Integer, ForeignKey('auth.district_group.district_group_id'))
    groups = Column(ARRAY(Integer))
    positions = Column(ARRAY(Integer))
    fio = Column(String)

    def as_dict(self):
        """Convert model instance to dictionary with serializable types"""
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            # Convert UUID to string
            if isinstance(value, uuid.UUID):
                result[c.name] = str(value)
            else:
                result[c.name] = value
        return result
