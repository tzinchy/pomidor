from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from fastapi.responses import JSONResponse
from fastapi.concurrency import run_in_threadpool
from service.spd1_service import Spd1Service
from depends import get_oracle_client

spd1_service = Spd1Service(client=get_oracle_client())


router = APIRouter(
    prefix="/spd1", tags=["SPD1"], 
)

@router.get("/update_data")
async def update_spd1_data():
    '''
    router for update scheduler
    just add "curl -X GET http://127.0.0.1:PORT/spd1/update_data" in the crontab
    '''
    result, detail = await spd1_service.update_data()
    return JSONResponse(content={"message": detail}, status_code=result)