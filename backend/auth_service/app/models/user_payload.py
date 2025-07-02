from sqlalchemy import Column, String, Integer, JSON, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
import uuid
from models.base import Base

class UserPayload(Base):
    __tablename__ = 'user_payload'
    __table_args__ = {'info': {'is_view': True}, 'schema': 'auth'}  # Указываем, что это VIEW
    
    # Поля согласно структуре вашего VIEW
    user_uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    roles_ids = Column(JSON)  # или ARRAY(Integer) для PostgreSQL
    roles = Column(JSON)      # или ARRAY(String) для PostgreSQL
    districts = Column(ARRAY(String))   # или ARRAY(String)
    groups_ids = Column(JSON)  # или ARRAY(Integer)
    groups_info = Column(JSON)
    positions_ids = Column(JSON)  # или ARRAY(Integer)
    positions_info = Column(JSON)
    telegram_token = Column(String)
    telegram_chat_id = Column(String)

    def __repr__(self):
        return f"<UserPayload(user_uuid='{self.user_uuid}', first_name='{self.first_name}')>"
    
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