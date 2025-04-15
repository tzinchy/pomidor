from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum
from schema.status import Status

class FamilyStructureSchema(BaseModel):
    affair_id: int = Field(..., description="ID дела")
    district: Optional[str] = Field(None, description="Район")
    house_address: Optional[str] = Field(None, description="Адрес дома")
    apart_number: Optional[str] = Field(None, description="Номер квартиры")

    class Config:
        orm_mode = True


class NewApartmentSchema(BaseModel):
    new_apart_id: int = Field(..., description="Id квартиры")
    district: str = Field(..., description="Район")
    municipal_district: float = Field(..., description="Площадь")
    house_address: str = Field(..., description="Адрес дома")


class ApartTypeSchema(str, Enum):
    NEW = "NewApartment"
    OLD = "OldApart"


class MatchingSchema(BaseModel):
    old_apartment_district: List[str] = None
    old_apartment_municipal_district: List[str] = None
    old_apartment_house_address: List[str] = None
    new_apartment_district: List[str] = None
    new_apartment_municipal_district: List[str] = None
    new_apartment_house_address: Optional[List] = None 
    is_date : bool = None

class RematchSchema(BaseModel):
    apartment_ids : List[int]

class ManualMatchingSchema(BaseModel):
    new_apart_ids : List[int]

class SetPrivateStatusSchema(BaseModel):
    new_apart_ids : List[int]

class SetStatusForNewAparts(BaseModel):
    apart_ids : List[int]
    status : Status

class SetSpecialNeedsSchema(BaseModel):
    apart_ids : List[int]
    is_special_needs_marker : int

class DeclineReasonSchema(BaseModel):
    min_floor: int = 0
    max_floor: int = 0
    unom: Optional[str] = None
    entrance: Optional[str] = None
    apartment_layout: Optional[str] = None
    notes: Optional[str] = None

class BaseApartmentTableSchema(BaseModel):
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

class OldApartTableSchema(BaseApartmentTableSchema):
    affair_id : Optional[int] = None,
    is_queue : Optional[str] = None

class NewApartTableSchema(BaseApartmentTableSchema):
    new_apart_id : Optional[int] = None,
    is_private : Optional[str] = None,
    apart_number: Optional[int] = None

class SetNotesSchema(BaseModel):
    notes : Optional[str] = None