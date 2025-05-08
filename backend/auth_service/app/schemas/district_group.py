from pydantic import BaseModel
from typing import List 

class DistrictGroupSchema(BaseModel):
    district_group_id : int 
    description : str
    districts_ids : List[int]

class DistrictGroupWithDistrictsSchema(DistrictGroupSchema):
    districts : List[str]

