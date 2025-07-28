from depends import cin_service
from service.auth import get_user
from fastapi import APIRouter, Depends, Query
from schema.cin import Cin, CreateCin
from schema.user import User
from schema.apartment import ApartType
from typing import Optional, List
router = APIRouter(prefix="/cin", tags=["Cin"])


@router.get("")

async def get_cin():
    return await cin_service.get_cin()


@router.patch("/update_cin")
async def udpate_cin(cin: Cin):
    return await cin_service.update_cin(cin)

@router.post("/create_cin")
async def create_cin(cin : CreateCin): 
    return await cin_service.create_cin(cin)


@router.get("/district")
async def get_districts(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
):  
    return await cin_service.get_cin_district(apart_type)


@router.get("/municipal_district")
async def get_areas(
    apart_type: ApartType = Query(None, description="Тип апартаментов"),
    district: Optional[List[str]] = Query(None, description="Список районов"),
):
    return await cin_service.get_cin_municipal_districts(apart_type, district)


@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    district : Optional[List[str]] = Query(None,),
    municipal_districts: Optional[List[str]] = Query(None,),
):
    return await cin_service.get_cin_house_addresses(apart_type, municipal_districts, district=district)