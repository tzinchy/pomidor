
from uuid import UUID

from pydantic import BaseModel

'''
class User(BaseModel):
    user_uuid: UUID
    roles_ids: Optional[List[int]] = None
    roles: Optional[List[RoleBase]] = None
    district_group_id: Optional[int] = None
    distircts: Optional[DistrictGroupWithDistricts] = None
    groups_ids: Optional[List[int]] = None
    groups: Optional[List[GroupWithActions]]
    positions_ids: Optional[List[int]] = None
    positions: Optional[PositionWithAllInfo] = None
    telegram_token : Optional[str] = None 
    telegram_chat_id : Optional[int] = None
'''
class UserUuid(BaseModel):
    user_uuid : UUID
