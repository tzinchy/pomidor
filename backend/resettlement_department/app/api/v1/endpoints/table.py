from fastapi import APIRouter, Query, HTTPException, Body
from depends import apartment_service
from schema.apartment import (
    ApartTypeSchema,
)
from typing import Optional, List, Literal



router = APIRouter(prefix="/tables", tags=["Table and Tree"])


# Получение текущего типа апартаментов
@router.get("/apart_type")
async def get_current_apart_type(
    apart_type: ApartTypeSchema = Query(
        default=ApartTypeSchema.NEW, description="Тип квартир"
    ),
):
    return {"apart_type": apart_type}


# Получение списка районов
@router.get("/district")
async def get_districts(
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    return await apartment_service.get_district(apart_type)


# Получение списка муниципальных районов
@router.get("/municipal_district")
async def get_areas(
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
    district: List[str] = Query(..., description="Список районов"),
):
    return await apartment_service.get_municipal_districts(apart_type, district)


# Получение списка адресов домов
@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
    municipal_district: List[str] = Query(..., description="Список областей"),
):
    return await apartment_service.get_house_addresses(apart_type, municipal_district)


@router.get("/apartments")
async def get_apartments(
    apart_type: ApartTypeSchema = Query(..., description="Тип квартиры"),
    house_addresses: Optional[List[str]] = Query(
        None, description="Список адресов домов"
    ),
    districts: Optional[List[str]] = Query(None, description="Фильтр по районам"),
    municipal_districts: Optional[List[str]] = Query(
        None, description="Фильтр по муниципальным округам"
    ),
    floor: Optional[int] = Query(None, description="Фильтр по этажу"),
    min_area: Optional[float] = Query(None, description="Минимальная площадь"),
    max_area: Optional[float] = Query(None, description="Максимальная площадь"),
    area_type: Literal["full_living_area", "total_living_area", "living_area"] = Query(
        "full_living_area", description="Тип площади для фильтрации"
    ),
    room_count: Optional[List[int]] = Query(
        None,
        description="Фильтр по количеству комнат (можно несколько значений)",
        example=[1, 2, 3],
    ),
    is_queue: bool = None,
    is_private: bool = None
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
            room_count=room_count,
            is_queue=is_queue,
            is_private=is_private,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/switch_aparts")
async def switch_apartments(
    first_apart_id: int = Body(..., description="ID первой квартиры"),
    second_apart_id: int = Body(..., description="ID второй квартиры"),
):
    await apartment_service.switch_apartment(first_apart_id, second_apart_id)

