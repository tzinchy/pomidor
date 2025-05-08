from pydantic import BaseModel

class District(BaseModel):
    district : str

class DistrictWithId(District):
    district_id : int 