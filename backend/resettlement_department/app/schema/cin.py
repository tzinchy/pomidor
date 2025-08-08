from datetime import datetime
from typing import Optional, Dict
from pydantic import BaseModel

class CINBase(BaseModel):
    unom: Optional[str] = None
    house_address: str
    district: str
    municipal_district: str
    cin_address: str
    cin_schedule: str
    dep_schedule: str
    phone_osmotr: str
    otdel: str
    phone_otvet: str
    manual_load_id: Optional[int] = None
    start_dates_by_entrence: Optional[Dict] = None
    full_cin_address: Optional[str] = None
    full_house_address: Optional[str] = None
    otsel_addresses_and_dates: Optional[Dict] = None

class CreateCin(CINBase):
    pass

class Cin(CINBase):
    cin_id: int

    class Config:
        orm_mode = True

