from fastapi import Depends, HTTPException, status
from schema.apartment import ApartTypeSchema
from typing import Annotated

def is_old_apart(apart_type: ApartTypeSchema):
    if apart_type != ApartTypeSchema.OLD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='IS NOT OLD APART')

old_apart_validator = Annotated[ApartTypeSchema, Depends(is_old_apart)]