from fastapi import APIRouter, Query, HTTPException, Body
from schema.apartment import (
    ApartTypeSchema,
    RematchSchema,
    ManualMatchingSchema,
    SetPrivateStatusSchema,
    SetPrivateStatusSchemaWithValue,
    DeclineReasonSchema,
    SetNotesSchema,
)
from schema.status import StatusUpdate
from service.rematch_service import rematch
from depends import apartment_service

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
def rematch_for_family(rematch_list: RematchSchema):
    res = rematch(rematch_list.apartment_ids)
    return {"res": res}


@router.post("/{apart_id}/{new_apart_id}/change_status")
async def change_status(
    apart_id: int,
    new_apart_id: int,
    new_status: StatusUpdate = Body(..., description="Доступные статусы"),
    apart_type: ApartTypeSchema = Query(..., description="Тип апартаментов"),
):
    try:
        await apartment_service.update_status_for_apart(
            apart_id, new_apart_id, new_status.new_status.value, apart_type
        )
        return {"message": "Status updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


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
    return await apartment_service.set_notes(apart_id, notes.notes, apart_type)

@router.patch("/set_private")
async def set_private_for_new_aparts(set_private_status: SetPrivateStatusSchemaWithValue):
    return await apartment_service.set_private_for_new_aparts(
        set_private_status.new_apart_ids, status=set_private_status.is_private
    )

@router.patch("/set_private_true")
async def set_private_for_new_aparts_true(new_aparts_ids: SetPrivateStatusSchema):
    return await apartment_service.set_private_for_new_aparts(
        new_aparts_ids.new_apart_ids, status=True
    )


@router.patch("/set_private_false")
async def set_private_for_new_aparts_false(new_apart_ids: SetPrivateStatusSchema):
    return await apartment_service.set_private_for_new_aparts(
        new_aparts=new_apart_ids.new_apart_ids, status=False
    )


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

