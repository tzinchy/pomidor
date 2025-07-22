from depends import cin_service
from service.auth_serivce import get_user
from fastapi import APIRouter, Depends
from schema.cin import Cin, CreateCin
from schema.user import User

router = APIRouter(prefix="/cin", tags=["Cin"])


@router.get("")
async def get_cin(user : User = Depends(get_user)):
    return await cin_service.get_cin(user.districts)


@router.patch("/update_cin")
async def udpate_cin(cin: Cin):
    return await cin_service.update_cin(cin)

@router.post("/create_cin")
async def create_cin(cin : CreateCin): 
    return await cin_service.create_cin(cin)


