from depends import apartment_service
from fastapi import APIRouter, Body, HTTPException, Query, Depends
from schema.apartment import (
    ApartType,
    DeclineReason,
    ManualMatching,
    Rematch,
    SetNotes,
    SetStatusForNewAparts,
    SetSpecialNeeds,
)
from schema.status import StatusUpdate
from service.rematch_service import rematch
from service.container_service import (
    generate_excel_from_two_dataframes,
    upload_container,
)
from service.container_service import update_apart_status
from service.auth import mp_employee_required, User

router = APIRouter(prefix="/tables/apartment", tags=["Apartment Action"])


@router.get("/{apart_id}")
async def get_apartment_by_id(
    apart_id: int,
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
):
    apartment = await apartment_service.get_apartment_by_id(apart_id, apart_type)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment


@router.get("/decline_reason/{decline_reason_id}")
async def get_decline_reason(decline_reason_id: int):
    return await apartment_service.get_decline_reason(decline_reason_id)


@router.get("/{apart_id}/void_aparts")
async def get_void_aparts_for_apartment(apart_id: int, user : User = Depends(mp_employee_required)):
    return await apartment_service.get_void_aparts_for_apartment(apart_id)

@router.post("/{apart_id}/manual_matching")
async def manual_matching(
    apart_id: int,
    manual_selection: ManualMatching = Body(
        ..., description="Передается списко new_apart_id"
    ),
    user : User = Depends(mp_employee_required)
):
    return await apartment_service.manual_matching(
        apart_id, manual_selection.new_apart_ids
    )


@router.post("/{apart_id}/cancell_matching_for_apart")
async def cancell_matching_for_apart(apart_id: int, apart_type: ApartType = Query(...), user : User = Depends(mp_employee_required)):
    return await apartment_service.cancell_matching_for_apart(apart_id, apart_type)


@router.post("/rematch")
async def rematch_for_family(rematch_list: Rematch, user : User = Depends(mp_employee_required)):
    res = await rematch(rematch_list.apartment_ids)
    return {"res": res}


@router.post("/{apart_id}/{new_apart_id}/change_status")
async def change_status(
    apart_id: int,
    new_apart_id: int,
    new_status: StatusUpdate = Body(...),
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
):
    try:
        print(new_status.new_status.value)
        res = await apartment_service.update_status_for_apart(
            apart_id=apart_id,
            new_apart_id=new_apart_id,
            status=new_status.new_status.value,
            apart_type=apart_type,
        )
        return res
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{apart_id}/{new_apart_id}/set_decline_reason")
async def set_cancell_reason(
    apart_id: int, new_apart_id: int, decline_reason: DeclineReason
):
    return await apartment_service.set_decline_reason(
        apart_id=apart_id,
        new_apart_id=new_apart_id,
        min_floor=decline_reason.min_floor,
        max_floor=decline_reason.max_floor,
        unom=decline_reason.unom,
        entrance=decline_reason.entrance,
        apartment_layout=decline_reason.apartment_layout,
        notes=decline_reason.notes,
    )


@router.post("/{apart_id}/set_notes")
async def set_notes(
    apart_id: int,
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    notes: SetNotes = None,
):
    """
    Проставляет поле notes и rsm_notes.
    Строка разбивается по ";".
    Первый элемент идет в rsm_notes, остальные в notes

    Можно использовать вместо этой ручки /tables/apartment/set_notes_for_many
    """
    return await apartment_service.set_notes_for_many(
        [apart_id], notes.notes, apart_type
    )


@router.patch("/decline_reason/{decline_reason_id}/update_declined_reason")
async def update_declined_reason(decline_reason_id: int, decline_reason: DeclineReason):
    return await apartment_service.update_decline_reason(
        decline_reason_id=decline_reason_id,
        min_floor=decline_reason.min_floor,
        max_floor=decline_reason.max_floor,
        unom=decline_reason.unom,
        entrance=decline_reason.entrance,
        apartment_layout=decline_reason.apartment_layout,
        notes=decline_reason.notes,
    )


@router.patch("/set_status_for_many")
async def set_consent(
    apart_ids_and_status: SetStatusForNewAparts,
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
):
    print(apart_ids_and_status.apart_ids, apart_ids_and_status.status)
    return await apartment_service.set_status_for_many(
        apart_ids_and_status.apart_ids, apart_ids_and_status.status, apart_type
    )


@router.patch("/set_special_needs_for_many")
async def set_special_needs_for_many(
    apart_ids_and_marker: SetSpecialNeeds,
):
    """
    Проставляет поле is_special_needs_marker. Это поле int и *не подвержено валидации*
    """
    return await apartment_service.set_special_needs_for_many(
        apart_ids_and_marker.apart_ids, apart_ids_and_marker.is_special_needs_marker
    )


@router.patch("/set_notes_for_many")
async def set_notes_for_many(
    apart_ids: list[int] = Body(..., description="Список apart_id"),
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    notes: SetNotes = None,
):
    """
    Проставляет поле notes и rsm_notes.
    Строка разбивается по ";".
    Первый элемент идет в rsm_notes, остальные в notes
    """
    return await apartment_service.set_notes_for_many(
        apart_ids, notes.notes, apart_type
    )


@router.patch("/push_container_for_aparts")
def push_container_for_aparts(apart_ids: Rematch):
    print(apart_ids.apartment_ids)
    generate_excel_from_two_dataframes(affair_ids=apart_ids.apartment_ids)
    #update_apart_status(apart_ids=apart_ids.apartment_ids)
    file_path = "./uploads/container_0.xlsx"
    #upload_container(history_id=0, file_path=file_path)


@router.patch("/set_district_notes_for_many")
async def set_district_notes_for_many(
    apart_ids: list[int] = Body(..., description="Список apart_id"),
    apart_type: ApartType = Query(..., description="Тип апартаментов"),
    notes: SetNotes = None,
):
    """
    Проставляет поле notes и rsm_notes.
    Строка разбивается по ";".
    Первый элемент идет в rsm_notes, остальные в notes
    """
    return await apartment_service.set_district_notes_for_many(
        apart_ids, notes.notes, apart_type
    )