from fastapi import APIRouter, Query, HTTPException, Depends
from service.apartment_service import ApartmentService, ApartTypeService

router = APIRouter(prefix="/tables", tags=["tables"])


@router.get("/apart_type")
async def get_current_apart_type():
    """
    Получить текущее значение `apart_type`.
    """
    return {"apart_type": ApartTypeService.get_apart_type()}


@router.post("/apart_type")
async def set_current_apart_type(apart_type: str = Query(..., description="Тип квартир")):
    """
    Установить новое значение `apart_type`.
    """
    try:
        ApartTypeService.set_apart_type(apart_type)
        return {"message": "Apartment type updated", "apart_type": apart_type}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/districts")
async def get_districts():
    """
    Получить список районов.
    """
    apart_type = ApartTypeService.get_apart_type()
    return await ApartmentService.get_districts(apart_type)


@router.get("/areas")
async def get_areas(
    districts: list[str] = Query(..., description="Список районов")
):
    """
    Получить список областей.
    """
    apart_type = ApartTypeService.get_apart_type()
    return await ApartmentService.get_areas(apart_type, districts)


@router.get("/house_addresses")
async def get_house_addresses(
    areas: list[str] = Query(..., description="Список областей")
):
    """
    Получить список адресов домов.
    """
    apart_type = ApartTypeService.get_apart_type()
    return await ApartmentService.get_house_addresses(apart_type, areas)
