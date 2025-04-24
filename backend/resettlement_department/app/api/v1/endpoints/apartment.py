from depends import apartment_service
from fastapi import APIRouter, Body, HTTPException, Query
from schema.apartment import (
    ApartTypeSchema,
    DeclineReasonSchema,
    ManualMatchingSchema,
    RematchSchema,
    SetNotesSchema,
    SetStatusForNewAparts,
    SetSpecialNeedsSchema,
)
from schema.status import Status, StatusUpdate
from service.rematch_service import rematch

router = APIRouter(prefix="/tables/apartment", tags=["Apartment Action"])


@router.get("/{apart_id}")
async def get_apartment_by_id(
    apart_id: int,
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    apartment = await apartment_service.get_apartment_by_id(apart_id, apart_type)
    if not apartment:
        raise HTTPException(status_code=404, detail="Apartment not found")
    return apartment


@router.get("/decline_reason/{decline_reason_id}")
async def get_decline_reason(decline_reason_id: int):
    return await apartment_service.get_decline_reason(decline_reason_id)


@router.get("/{apart_id}/void_aparts")
async def get_void_aparts_for_apartment(apart_id: int):
    return await apartment_service.get_void_aparts_for_apartment(apart_id)


@router.post("/{apart_id}/manual_matching")
async def manual_matching(
    apart_id: int,
    manual_selection: ManualMatchingSchema = Body(
        ..., description="Передается списко new_apart_id"
    ),
):
    return await apartment_service.manual_matching(
        apart_id, manual_selection.new_apart_ids
    )


@router.post("/{apart_id}/cancell_matching_for_apart")
async def cancell_matching_for_apart(
    apart_id: int, apart_type: ApartTypeSchema = Query(...)
):
    return await apartment_service.cancell_matching_for_apart(apart_id, apart_type)


@router.post("/rematch")
async def rematch_for_family(rematch_list: RematchSchema):
    res = await rematch(rematch_list.apartment_ids)
    return {"res": res}


@router.post("/{apart_id}/{new_apart_id}/change_status")
async def change_status(
    apart_id: int,
    new_apart_id: int,
    new_status: StatusUpdate = Body(...),
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    try:
        print(new_status.new_status.value)
        await apartment_service.update_status_for_apart(
            apart_id=apart_id, new_apart_id=new_apart_id, status=new_status.new_status.value, apart_type=apart_type
        )
        return {"message": "Status updated successfully"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/change_status_for_new_apart")
async def change_status_for_new_apart(
    new_apart_ids: list[int] = Body(..., description="Список new_apart_id"),
    new_status: Status = Body(..., description="Доступные статусы"),
):
    print(new_status)
    return await apartment_service.update_status_for_apart(
        new_apart_ids, new_status.value
    )


@router.post("/{apart_id}/{new_apart_id}/set_decline_reason")
async def set_cancell_reason(
    apart_id: int, new_apart_id: int, decline_reason: DeclineReasonSchema
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
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
    notes: SetNotesSchema = None,
):
    return await apartment_service.set_notes_for_many([apart_id], notes.notes, apart_type)

@router.patch("/decline_reason/{decline_reason_id}/update_declined_reason")
async def update_declined_reason(
    decline_reason_id: int, decline_reason: DeclineReasonSchema
):
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
    apart_ids_and_status : SetStatusForNewAparts,
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    print(apart_ids_and_status.apart_ids, apart_ids_and_status.status.value)
    return await apartment_service.set_status_for_many(
        apart_ids_and_status.apart_ids, apart_ids_and_status.status.value, apart_type
    )

@router.patch("/set_special_needs_for_many")
async def set_special_needs_for_many(
    apart_ids_and_marker : SetSpecialNeedsSchema,
):
    return await apartment_service.set_special_needs_for_many(
        apart_ids_and_marker.apart_ids, apart_ids_and_marker.is_special_needs_marker
    )

@router.patch("/set_notes_for_many")
async def set_notes_for_many(
    apart_ids: list[int] = Body(..., description="Список apart_id"),
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
    notes: SetNotesSchema = None,
):
    return await apartment_service.set_notes_for_many(apart_ids, notes.notes, apart_type)
