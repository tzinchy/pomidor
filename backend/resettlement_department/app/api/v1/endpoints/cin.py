from depends import cin_service
from fastapi import APIRouter

router = APIRouter(prefix="/cin", tags=["Cin"])

@router.get('')
async def get_cin():
    return await cin_service.get_cin()