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
    up_id: int = Field(..., description="Идентификатор уникального пользователя")
    district: str = Field(..., description="Район")
    area: float = Field(..., description="Площадь")
    house_address: str = Field(..., description="Адрес дома")


class ApartType(str, Enum):
    NEW = "NewApartment"
    OLD = "FamilyStructure"


class MatchingSchema(BaseModel):
    family_structure_district: List[str] = None
    family_structure_municipal_district: List[str] = None
    family_structure_house_address: List[str] = None
    new_apartment_district: List[str] = None
    new_apartment_municipal_district: List[str] = None
    new_apartment_house_address: List[str] = None 



