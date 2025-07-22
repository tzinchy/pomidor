from sqlalchemy import Column, String, Integer, JSON
from sqlalchemy.dialects.postgresql import UUID as PG_UUID, ARRAY
import uuid
from models.base import Base

class UserFrontendPayload(Base):
    __tablename__ = 'user_frontend_payload'
    __table_args__ = {'info': {'is_view': True}, 'schema': 'auth'}
    
    user_uuid = Column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    first_name = Column(String)
    middle_name = Column(String)
    last_name = Column(String)
    roles = Column(ARRAY(String)) 
    districts = Column(ARRAY(String))  
    groups_info = Column(JSON)
    positions_info = Column(JSON)

    def as_dict(self):
        """Convert model instance to dictionary"""
        return {
            'user_uuid': str(self.user_uuid),
            'first_name': self.first_name,
            'middle_name': self.middle_name,
            'last_name': self.last_name,
            'roles': self.roles,
            'districts': self.districts,
            'groups_info': self.groups_info,
            'positions_info': self.positions_info
        }