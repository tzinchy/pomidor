from typing import List, Literal, Optional

from depends import apartment_service, order_service
from fastapi import APIRouter, Body, HTTPException, Query
from schema.apartment import ApartTypeSchema

router = APIRouter(prefix="/tables", tags=["Table and Tree"])

@router.get("/apart_type")
async def get_current_apart_type(
    apart_type: ApartTypeSchema = Query(
        default=ApartTypeSchema.NEW, description="Получить тип апартаментов (старая(семья)/новая(ресурс))"
    ),
):
    return {"apart_type": apart_type}

@router.get("/district")
async def get_districts(
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    return await apartment_service.get_district(apart_type)

@router.get("/municipal_district")
async def get_areas(
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
    district: List[str] = Query(..., description="Список районов"),
):
    return await apartment_service.get_municipal_districts(apart_type, district)

@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
    municipal_districts: Optional[List[str]] = Query(...),
):
    return await apartment_service.get_house_addresses(apart_type, municipal_districts)

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

@router.get("/apartments_one_json")
async def get_apartments_one_json(
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
    try:
        return await apartment_service.get_apartments_one_json(
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

@router.get("/get_entrance_ranges")
async def get_entrance_number_new_apart(
    house_address: str = Query(
        None, description="Адрес дома"
    )
):
    return await apartment_service.get_entrance_ranges(house_address)

@router.patch("/set_entrance_number_for_many")
async def set_entrance_number_for_many(
    new_apart_ids: List[int] = Body(..., description="Список new_apart_id"),
    entrance_number: int = Body(..., description="Номер подъезда")
):
    return await apartment_service.set_entrance_number_for_many(new_apart_ids, entrance_number)

@router.get("/old_apart")
async def old_apart():
    return await apartment_service.get_excel_old_apart()

@router.get("/new_apart")
async def new_apart():
    return await apartment_service.get_excel_new_apart()

@router.get("/order_decisions")
async def order_decisions():
    return await order_service.get_excel_order()
