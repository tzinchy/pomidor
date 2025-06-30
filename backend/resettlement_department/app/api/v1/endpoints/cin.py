from depends import cin_service
from fastapi import APIRouter
from schema.cin import Cin, CreateCin

router = APIRouter(prefix="/cin", tags=["Cin"])


@router.get("")
async def get_cin():
    return await cin_service.get_cin()


@router.patch("/update_cin")
async def udpate_cin(cin: Cin):
    return await cin_service.update_cin(cin)

@router.post("/create_cin")
async def create_cin(cin : CreateCin): 
    return await cin_service.create_cin(cin)


