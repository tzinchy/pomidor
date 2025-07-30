from depends import mail_index_service
from schema.mail_index import MailIndexCreate, MailIndexUpdate, MailIndexTable
from fastapi import APIRouter


router = APIRouter(prefix="/mail_index", tags=["mail_index"])

@router.get("")
async def mail_index():
    return await mail_index_service.get_mail_index()


@router.patch("/update_mail_index")
async def udpate_cin(mail_index: MailIndexUpdate):
    return await mail_index_service.update_mail_index(mail_index)

@router.post("/create_mail_index", response_class=MailIndexTable)
async def create_cin(mail_index : MailIndexCreate): 
    return await mail_index_service.create_mail_index(mail_index)


