from pydantic import BaseModel
from typing import Optional, List

class UserTokenData(BaseModel):
    user_uuid: str
    roles_ids: List[int] = []
    district_group_id: Optional[int] = None
    groups_ids: List[int] = []
    positions_ids: List[int] = []
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    districts_ids: List[int] = []
    exp: int