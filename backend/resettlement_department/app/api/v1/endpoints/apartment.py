from fastapi import APIRouter, Query, HTTPException
from depends import apartment_service
from schema.apartment import ApartType
from typing import Optional, List, Literal
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
    return await apartment_service.get_district(apart_type)


# Получение списка муниципальных районов
@router.get("/municipal_district")
async def get_areas(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    district: list[str] = Query(..., description="Список районов")
):
    return await apartment_service.get_municipal_districts(apart_type, district)


# Получение списка адресов домов
@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    municipal_district: list[str] = Query(..., description="Список областей")
):
    return await apartment_service.get_house_addresses(apart_type, municipal_district)


@router.get('/apartments')
async def get_apartments(
    apart_type: ApartType = Query(..., description='Тип квартиры'),
    house_addresses: Optional[List[str]] = Query(None, description='Список адресов домов'),
    districts: Optional[List[str]] = Query(None, description='Фильтр по районам'),
    municipal_districts: Optional[List[str]] = Query(None, description='Фильтр по муниципальным округам'),
    floor: Optional[int] = Query(None, description='Фильтр по этажу'),
    min_area: Optional[float] = Query(None, description='Минимальная площадь'),
    max_area: Optional[float] = Query(None, description='Максимальная площадь'),
    area_type: Literal['full_living_area', 'total_living_area', 'living_area'] = Query(
        'full_living_area', 
        description='Тип площади для фильтрации'
    ),
    room_count: Optional[List[int]] = Query(  # Добавляем новый параметр
        None, 
        description='Фильтр по количеству комнат (можно несколько значений)',
        example=[1, 2, 3]
    )
):
    """
    Получить отфильтрованный список квартир с возможностью фильтрации по:
    - Типу квартир (обязательный параметр)
    - Адресам домов
    - Районам
    - Муниципальным округам
    - Этажу
    - Диапазону площадей
    - Количеству комнат
    """
    try:
        return await apartment_service.get_apartments(
            apart_type=apart_type,
            house_addresses=house_addresses,
            districts=districts,
            municipal_districts=municipal_districts,
            floor=floor,
            min_area=min_area,
            max_area=max_area,
            area_type=area_type,
            room_count=room_count  # Передаем новый параметр
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

# Получение информации по конкретному апартаменту
@router.get("/apartment/{apartment_id}")
async def get_apartment_by_id(
    apartment_id: int, 
    apart_type: ApartType = Query(..., description="Тип апартаментов")
):

    apartment = await apartment_service.get_apartment_by_id(apartment_id, apart_type)
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

@router.post("/switch_aparts")
async def switch_apartments(
    first_apart_id : int, 
    second_apart_id : int
):
    return await apartment_service.switch_apartment(first_apart_id, second_apart_id)
