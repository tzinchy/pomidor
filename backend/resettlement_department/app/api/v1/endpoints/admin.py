from depends import offer_service
from fastapi import APIRouter

router = APIRouter(prefix="/admin", tags=["Admin action"])


@router.patch("/use_sync_offer_status_strict")
async def user_sync_offer_status_strict():
    return await offer_service.use_strict_update_offer_status()

