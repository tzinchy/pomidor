from fastapi import APIRouter, Query, HTTPException, Body
from depends import apartment_service
from schema.apartment import (
    ApartTypeSchema,
    RematchSchema,
    ManualMatchingSchema,
    SetPrivateStatusSchema,
    DeclineReasonSchema,
)
from service.rematch_service import rematch
from typing import Optional, List, Literal
from schema.status import StatusUpdate


router = APIRouter(prefix="/tables", tags=["Дерево"])


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
    is_private: bool = None,
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


# Получение информации по конкретному апартаменту
@router.get("/apartment/{apartment_id}")
async def get_apartment_by_id(
    apartment_id: int,
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    apartment = await apartment_service.get_apartment_by_id(apartment_id, apart_type)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment


@router.post("/apartment/{apartment_id}/manual_matching")
async def manual_matching(
    apartment_id: int,
    manual_selection: ManualMatchingSchema = Body(
        ..., description="Схема для ручного сопоставления"
    ),
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    return await apartment_service.manual_matching(
        apartment_id, manual_selection.new_apart_id
    )


@router.get("/apartment/{apartment_id}/void_aparts")
async def get_void_aparts_for_apartment(apartment_id: int):
    return await apartment_service.get_void_aparts_for_apartment(apartment_id)


@router.post("/apartment/{apartment_id}/cancell_matching_for_apart")
async def cancell_matching_for_apart(
    apartment_id: int, apart_type: ApartTypeSchema = Query(...)
):
    return await apartment_service.cancell_matching_for_apart(apartment_id, apart_type)


@router.post("/switch_aparts")
async def switch_apartments(
    first_apart_id: int = Body(..., description="ID первой квартиры"),
    second_apart_id: int = Body(..., description="ID второй квартиры"),
):
    await apartment_service.switch_apartment(first_apart_id, second_apart_id)


@router.post("/apartment/rematch")
def rematch_for_family(rematch_list: RematchSchema):
    res = rematch(rematch_list.apartment_ids)
    return {"res": res}


@router.post("/apartment/{apartment_id}/change_status")
async def change_status(
    apartment_id: int,
    new_status: StatusUpdate = Body(..., description="Доступные статусы"),
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    try:
        await apartment_service.update_status_for_apart(
            apartment_id, new_status.new_status.value, apart_type
        )
        return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("/apartment/set_private_true")
async def set_private_for_new_aparts_true(new_aparts_ids: SetPrivateStatusSchema):
    return await apartment_service.set_private_for_new_aparts(
        new_aparts_ids.new_apart_ids, status=True
    )


@router.patch("apartment/set_private_falce")
async def set_private_for_new_aparts_false(new_apart_ids: SetPrivateStatusSchema):
    return await apartment_service.set_private_for_new_aparts(
        new_aparts=new_apart_ids.new_apart_ids, status=False
    )


@router.post("/apartment/{apartment_id}/set_cancell_reason")
async def set_cancell_reason(apartment_id: int, decline_reason: DeclineReasonSchema):
    await apartment_service.set_cancell_reason(
        apartment_id,
        decline_reason.min_floor,
        decline_reason.max_floor,
        decline_reason.unom,
        decline_reason.entrance,
        decline_reason.apartment_layout,
        decline_reason.notes,
    )
