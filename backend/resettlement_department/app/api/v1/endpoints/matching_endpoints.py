from fastapi import APIRouter, Query, Body
from service.apartment_service import ApartmentService
from models.apartment import ApartType, MatchingSchema

router = APIRouter(prefix="/mathing", tags=["Первичный подбор"])


# Получение списка районов
@router.get("/family_structure/district")
async def get_family_structure_districts(
):
    return await ApartmentService.get_district(apart_type=ApartType.OLD)


# Получение списка муниципальных районов
@router.get("/family_structure/municipal_district")
async def get_family_structure_areas(
    municipal_district: list[str] = Query(..., description="Список районов")
):
    return await ApartmentService.get_municipal_districts(apart_type=ApartType.OLD, municipal_district=municipal_district)


# Получение списка адресов домов
@router.get("/family_structure/house_addresses")
async def get_family_structure_house_addresses(
    areas: list[str] = Query(..., description="Список областей")
):
    return await ApartmentService.get_house_addresses(apart_type=ApartType.OLD, areas=areas)


# Получение списка районов
@router.get("/new_apartment/district")
async def get_new_apartment_districts(
):
    return await ApartmentService.get_district(apart_type=ApartType.NEW)


# Получение списка муниципальных районов
@router.get("/new_apartment/municipal_district")
async def get_new_apartment_areas(
    municipal_district: list[str] = Query(..., description="Список районов")
):
    return await ApartmentService.get_municipal_districts(apart_type=ApartType.NEW, municipal_district=municipal_district)


# Получение списка адресов домов
@router.get("/new_apartment/house_addresses")
async def get_new_apartment_house_addresses(
    areas: list[str] = Query(..., description="Список областей")
):
    return await ApartmentService.get_house_addresses(apart_type=ApartType.NEW, area=areas)

@router.post('/matching')
async def start_matching(
    requirements: MatchingSchema = Body(...)
):
    return {"message": "Matching process started", "requirements": requirements.model_dump()}