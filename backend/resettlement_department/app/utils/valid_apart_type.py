from fastapi import Depends, HTTPException, status
from schema.apartment import ApartType
from typing import Annotated

def is_old_apart(apart_type: ApartType):
    if apart_type != ApartType.OLD:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail='IS NOT OLD APART')

old_apart_validator = Annotated[ApartType, Depends(is_old_apart)]