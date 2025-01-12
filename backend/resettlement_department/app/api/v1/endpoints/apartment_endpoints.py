from fastapi import APIRouter, Query, HTTPException
from service.apartment_service import ApartmentService
from models.apartment import ApartType

router = APIRouter(prefix="/tables", tags=["Дерево"])

# Получение текущего типа апартаментов
@router.get("/apart_type")
async def get_current_apart_type(
    apart_type: ApartType = Query(default=ApartType.NEW, description="Тип квартир")
):
    return {"apart_type": apart_type}


# Получение списка районов
@router.get("/district")
async def get_districts(
    apart_type: ApartType = Query(..., description="Тип апартаментов")
):
    return await ApartmentService.get_district(apart_type)


# Получение списка муниципальных районов
@router.get("/municipal_district")
async def get_areas(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    municipal_district: list[str] = Query(..., description="Список районов")
):
    return await ApartmentService.get_municipal_districts(apart_type, municipal_district)


# Получение списка адресов домов
@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    areas: list[str] = Query(..., description="Список областей")
):
    return await ApartmentService.get_house_addresses(apart_type, areas)


@router.get('/apartments')
async def get_apartments(
    apart_type : ApartType = Query(..., description='Тип квартиры'),
    house_addresses : list[str] = Query(..., description='Список улиц')
):
    return await ApartmentService.get_apartments(apart_type, house_addresses)


# Получение информации по конкретному апартаменту
@router.get("/apartment/{apartment_id}")
async def get_apartment_by_id(
    apartment_id: int, 
    apart_type: ApartType = Query(..., description="Тип апартаментов")
):

    apartment = await ApartmentService.get_apartment_by_id(apartment_id, apart_type)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment

@router.post("/apartment/{apartment_id}/rematch")
async def rematch_for_family(
    apartment_id: int,  
    apart_type: ApartType = Query(
        ApartType.OLD, description="Только старые квартиры разрешены"
    )
):
    if apart_type != ApartType.OLD:
        raise HTTPException(status_code=400, detail="Переподбор доступен только для старых квартир")
    return {"res": "Позже здесь будет вызываться функция переподбора", "apartment_id": apartment_id}
