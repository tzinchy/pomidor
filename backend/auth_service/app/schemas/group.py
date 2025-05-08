from pydantic import BaseModel
from typing import List 

class GroupSchema(BaseModel):
    group_id : int
    group : str 
    service_table : str
    pemissions_ids : List[int]

class GroupWithActionsSchema(GroupSchema):
    pemissions : List[str]
