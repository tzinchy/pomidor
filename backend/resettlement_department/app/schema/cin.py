import datetime

from pydantic import BaseModel


class Cin(BaseModel):
    cin_id: int
    unom: str
    house_address: str
    district : str
    municipal_district : str
    cin_address: str
    cin_schedule: str
    dep_schedule: str
    phone_osmotr: str
    phone_otvet : str
    otdel: str
    start_dates_by_entrence: dict
    phone_otvet: str

class CreateCin(BaseModel):
    unom: str
    old_address: str
    cin_address: str
    cin_schedule: str
    dep_schedule: str
    phone_osmotr: str
    otdel: str
    start_date: datetime.date
    phone_otvet: str
    district : str
    municipal_district : str
    start_dates_by_entrence : dict