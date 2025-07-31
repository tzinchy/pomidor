from typing import List, Literal, Optional

from fastapi.responses import FileResponse
from fastapi.concurrency import run_in_threadpool
from depends import apartment_service, order_service, offer_service
from fastapi import APIRouter, Body, HTTPException, Query, Depends
from schema.apartment import ApartType
from schema.user import User
from service.auth import get_user

router = APIRouter(prefix="/tables", tags=["Table and Tree"])


@router.get("/apart_type")
async def get_current_apart_type(
    apart_type: ApartType = Query(
        default=ApartType.NEW,
        description="Получить тип апартаментов (старая(семья)/новая(ресурс))",
    ),
):
    return {"apart_type": apart_type}


@router.get("/district")
async def get_districts(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    user: User = Depends(get_user),
):
    return await apartment_service.get_district(apart_type, user=user)


@router.get("/municipal_district")
async def get_areas(
    apart_type: ApartType = Query(None, description="Тип апартаментов"),
    district: Optional[List[str]] = Query(None, description="Список районов"),
):
    return await apartment_service.get_municipal_districts(apart_type, district)


@router.get("/house_addresses")
async def get_house_addresses(
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    district: Optional[List[str]] = Query(
        None,
    ),
    municipal_districts: Optional[List[str]] = Query(
        None,
    ),
):
    return await apartment_service.get_house_addresses(
        apart_type, municipal_districts, district=district
    )


@router.get("/apartments")
async def get_apartments(
    apart_type: ApartType = Query(..., description="Тип квартиры"),
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
    statuses: Optional[List[str]] = Query(None, example=["Свободная"]),
    fio: str = Query(None, example="Иванов"),
    stage: Optional[List[str]] = Query(None, example=["Не начато"]),
    otsel_type: Optional[List[str]] = Query(None, example=["Полное переселение"]),
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
            statuses=statuses,
            fio=fio,
            stage=stage,
            otsel_type=otsel_type,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/get_entrance_ranges")
async def get_entrance_number_new_apart(
    house_address: str = Query(None, description="Адрес дома"),
):
    return await apartment_service.get_entrance_ranges(house_address)


@router.get("/old_apart")
async def old_apart():
    """
    Выгрузка таблицы old_apart в Excel файл
    """
    result = await apartment_service.get_excel_old_apart()
    if filepath := result.get("filepath"):
        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="old_apart.xlsx",
        )
    else:
        return result


@router.get("/new_apart")
async def new_apart():
    """
    Выгрузка таблицы new_apart в Excel файл
    """
    result = await apartment_service.get_excel_new_apart()
    if filepath := result.get("filepath"):
        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="new_apart.xlsx",
        )
    else:
        return result


@router.get("/order_decisions")
async def order_decisions():
    """
    Выгрузка таблицы order_decisions в Excel файл
    """
    result = await order_service.get_excel_order()
    if filepath := result.get("filepath"):
        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="order_decisions.xlsx",
        )
    else:
        return result


@router.get("/offer_result")
async def offer():
    "Выгрузка таблицы offer в Excel файл"
    result = await offer_service.get_excel_offer()
    if filepath := result.get("filepath"):
        return FileResponse(
            path=filepath,
            media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            filename="offer.xlsx",
        )
    else:
        return result


@router.get("/get_stat")
async def get_stat():
    return await order_service.get_stat()


@router.post("/switch_aparts")
async def switch_apartments(
    first_apart_id: int = Body(..., description="ID первой квартиры"),
    second_apart_id: int = Body(..., description="ID второй квартиры"),
):
    await apartment_service.switch_apartment(first_apart_id, second_apart_id)


@router.patch("/set_entrance_number_for_many")
async def set_entrance_number_for_many(
    new_apart_ids: List[int] = Body(..., description="Список new_apart_id"),
    entrance_number: int = Body(..., description="Номер подъезда"),
):
    """
    Проставляет поле entrance_number у new_apart
    """
    return await apartment_service.set_entrance_number_for_many(
        new_apart_ids, entrance_number
    )


@router.get("/curent_table", response_class=FileResponse)
async def get_current_table(
    apart_type: ApartType = Query(...),
    apart_ids: List[int] = Query(...),
    with_last_offer: Optional[bool] = Query(...),
):
    return await apartment_service.get_current_table(
        apart_type=apart_type, apart_ids=apart_ids, with_last_offer=with_last_offer
    )
