from pydantic import BaseModel
from typing import Optional, List, Dict
from uuid import UUID

class User(BaseModel):
    user_uuid: str
    roles_ids: List[int] = []
    groups_ids: List[int] = []
    positions_ids: List[int] = []
    telegram_token: Optional[str] = None
    telegram_chat_id: Optional[int] = None
    districts: List[str] = []
    exp: int

class Group(BaseModel):
    group: str
    actions: List[str]

class ReportsTo(BaseModel):
    division: str
    position: str
    management: str
    position_id: int

class UserInfo(BaseModel):
    division: str
    position: str
    management: str
    reports_to: ReportsTo

class UserFrontedPayload(BaseModel):
    first_name: str
    middle_name: Optional[str] = None  
    last_name: str
    roles: List[str]
    districts: List[str]
    groups_info: Dict[str, Group]
    user_info: Optional[Dict[str, UserInfo]] = None
    user_id: Optional[str] = None  

class Districts(BaseModel):
    districts: Optional[List[str]] = None

class UserUuid(BaseModel):
    user_uuid : UUID

class PasswordSwitch(BaseModel):
    old_password : str 
    new_password : str 

