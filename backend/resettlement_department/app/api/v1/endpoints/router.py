from fastapi import APIRouter, Query, HTTPException, Depends
from sqlalchemy import select
from repository.database import async_session_maker
from service.apartment import ApartTypeService
from models.apartment import FamilyStructureBase, NewApartment
from typing import List, Optional
from JWTs import DecodeJWT
from pydantic import BaseModel
from models.user import UserJWTData


get_current_user = DecodeJWT(UserJWTData)

router = APIRouter(prefix="/tables", tags=["/tables"], dependencies=[Depends(get_current_user)])

class ApartTypeResponse(BaseModel):
    apart_type: str

@router.get("/apart_type", response_model=ApartTypeResponse)
async def get_current_apart_type():
    """Get the current apartment type."""
    return {"apart_type": ApartTypeService.get_apart_type()}

@router.post("/apart_type", response_model=ApartTypeResponse)
async def set_current_apart_type(apart_type: str):
    """Set the current apartment type."""
    try:
        ApartTypeService.set_apart_type(apart_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return {"apart_type": apart_type}

@router.get("/districts")
async def get_districts(
    apart_type: str = Depends(ApartTypeService.get_apart_type),
    user=Depends(get_current_user)
):
    async with async_session_maker() as session:
        model = FamilyStructureBase if apart_type == "FamilyStructure" else NewApartment
        result = await session.execute(select(model.district).distinct())
        districts = result.scalars().all()
    return districts

@router.get("/areas")
async def get_areas(
    apart_type: str = Depends(ApartTypeService.get_apart_type),
    districts: Optional[List[str]] = Query(None)
):
    async with async_session_maker() as session:
        model = FamilyStructureBase if apart_type == "FamilyStructure" else NewApartment
        query = select(model.area).distinct()
        if districts:
            query = query.filter(model.district.in_(districts))
        result = await session.execute(query)
        areas = result.scalars().all()
    return areas

@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: str = Depends(ApartTypeService.get_apart_type),
    districts: Optional[List[str]] = Query(None),
    areas: Optional[List[str]] = Query(None)
):
    async with async_session_maker() as session:
        model = FamilyStructureBase if apart_type == "FamilyStructure" else NewApartment
        query = select(model.house_address).distinct()
        if districts:
            query = query.filter(model.district.in_(districts))
        if areas:
            query = query.filter(model.area.in_(areas))
        result = await session.execute(query)
        house_addresses = result.scalars().all()
    return house_addresses

@router.get("/results")
async def get_apartments(
    apart_type: str = Depends(ApartTypeService.get_apart_type),
    districts: Optional[List[str]] = Query(None),
    areas: Optional[List[str]] = Query(None),
    addresses: Optional[List[str]] = Query(None)
):
    async with async_session_maker() as session:
        model = FamilyStructureBase if apart_type == "FamilyStructure" else NewApartment
        query = select(model)

        if districts:
            query = query.filter(model.district.in_(districts))

        if areas:
            query = query.filter(model.area.in_(areas))

        if addresses:
            query = query.filter(model.house_address.in_(addresses))

        result = await session.execute(query)
        apartments = result.scalars().all()
    return apartments

@router.get("/results/{apartment_id}")
async def get_apartment_by_id(
    apartment_id: int,  # Параметр без значения по умолчанию идет первым
    apart_type: str = Depends(ApartTypeService.get_apart_type)  # Параметры с дефолтными значениями идут после
):
    async with async_session_maker() as session:
        model = FamilyStructureBase if apart_type == "FamilyStructure" else NewApartment
        query = select(model).where(model.affair_id == apartment_id if apart_type == "FamilyStructure" else model.up_id == apartment_id)
        result = await session.execute(query)
        apartment = result.scalars().first()
        if apartment:
            return apartment
        else:
            raise HTTPException(status_code=404, detail="Apartment not found")
