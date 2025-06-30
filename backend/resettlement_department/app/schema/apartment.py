from enum import Enum
from typing import List, Optional

from pydantic import BaseModel, Field


class FamilyStructure(BaseModel):
    affair_id: int = Field(..., description="ID дела")
    district: Optional[str] = Field(None, description="Район")
    house_address: Optional[str] = Field(None, description="Адрес дома")
    apart_number: Optional[str] = Field(None, description="Номер квартиры")

    class Config:
        orm_mode = True


class NewApartment(BaseModel):
    new_apart_id: int = Field(..., description="Id квартиры")
    district: str = Field(..., description="Район")
    municipal_district: float = Field(..., description="Площадь")
    house_address: str = Field(..., description="Адрес дома")


class ApartType(str, Enum):
    NEW = "NewApartment"
    OLD = "OldApart"


class Matching(BaseModel):
    old_apartment_district: List[str] = None
    old_apartment_municipal_district: List[str] = None
    old_apartment_house_address: List[str] = None
    new_apartment_district: List[str] = None
    new_apartment_municipal_district: List[str] = None
    new_apartment_house_address: Optional[List] = None 
    is_date : bool = None

class Rematch(BaseModel):
    apartment_ids : List[int]

class ManualMatching(BaseModel):
    new_apart_ids : List[int]

class SetPrivateStatus(BaseModel):
    new_apart_ids : List[int]

class SetStatusForNewAparts(BaseModel):
    apart_ids : List[int]
    status : str

class SetSpecialNeeds(BaseModel):
    apart_ids : List[int]
    is_special_needs_marker : int

class DeclineReason(BaseModel):
    min_floor: int = 0
    max_floor: int = 0
    unom: Optional[str] = None
    entrance: Optional[str] = None
    apartment_layout: Optional[str] = None
    notes: Optional[str] = None

class BaseApartmentTable(BaseModel):
    offer_id : Optional[int] = None,         
    house_address : Optional[str] = None,
    apart_number : Optional[str] = None,
    district: Optional[str] = None,
    municipal_district : Optional[str] = None,
    floor : Optional[int] = None,
    fio : Optional[str] = None,
    full_living_area : Optional[float] = None,
    total_living_area : Optional[float] = None,
    living_area : Optional[float] = None,
    room_count : Optional[int] = None,
    type_of_settlement : Optional[str] = None,
    status : Optional[str] = None,
    notes : Optional[str] = None,
    rn : Optional[int] = None,
    selection_count : Optional[int] = None

class OldApartTable(BaseApartmentTable):
    affair_id : Optional[int] = None,
    is_queue : Optional[str] = None

class NewApartTable(BaseApartmentTable):
    new_apart_id : Optional[int] = None,
    is_private : Optional[str] = None,
    apart_number: Optional[int] = None

class SetNotes(BaseModel):
    notes : Optional[str] = None


class Balance(BaseModel):
    history_id : int 
    is_date : bool = None
    is_wave : Optional[bool] = None