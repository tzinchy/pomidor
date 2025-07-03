from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
import uuid
from models.base import Base

class UserBackendPayload(Base):
    __tablename__ = 'user_backend_payload'
    __table_args__ = {
        'info': {'is_view': True},
        'schema': 'auth'
    }
    
    user_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    roles_ids = Column(JSON)
    groups_ids = Column(JSON)
    positions_ids = Column(JSON)
    telegram_token = Column(String)
    telegram_chat_id = Column(String)
    districts = Column(ARRAY(String))
    
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
    
