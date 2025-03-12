from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


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


class MatchingSchema(BaseModel):
    old_apartment_district: List[str] = None
    old_apartment_municipal_district: List[str] = None
    old_apartment_house_address: List[str] = None
    new_apartment_district: List[str] = None
    new_apartment_municipal_district: List[str] = None
    new_apartment_house_address: List[str] = None 
    is_date : bool = None

class Rematch(BaseModel):
    apartment_ids : List[int]

class ManualMatchingSchema(BaseModel):
    new_apart_id : int

class SetPrivateStatusSchema(BaseModel):
    new_apart_ids : List[int]
    
