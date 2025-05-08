from pydantic import BaseModel

class PositionListBase(BaseModel):
    position : str

class PositionListWithId(PositionListBase):
    position_list_id : int 
