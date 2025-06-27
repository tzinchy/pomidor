import datetime

from pydantic import BaseModel


class Cin(BaseModel):
    cin_id: int
    unom: str
    old_address: str
    cin_address: str
    cin_schedule: str
    dep_schedule: str
    phone_osmotr: str
    otdel: str
    start_date: datetime.date
    phone_otvet: str
