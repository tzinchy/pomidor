from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import UUID, JSON, ARRAY
import uuid
from models.base import Base

class SubordinatesByUuid(Base):
    __tablename__ = 'subordinates_by_uuid'
    __table_args__ = {
        'info': {'is_view': True},
        'schema': 'auth'
    }
    
    user_uuid = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    subordinates = Column(ARRAY(UUID))

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
    
