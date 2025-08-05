from fastapi import APIRouter, File, HTTPException, UploadFile, Depends
from fastapi.concurrency import run_in_threadpool
from repository.oracledb import OracleClient
from depends import get_oracle_client


router = APIRouter(
    prefix="/spd1", tags=["SPD1"], 
)

@router.get("/test")
async def test_spd1(client: OracleClient = Depends(get_oracle_client)):

    return await run_in_threadpool(client.fetchall, "SELECT a.appid, a.APPNAME, a.APPDATE, a.PGUDATE, a.MODUSER, a.MODCOMP, sdk.actdocnum, f.CADNUM, a2.DOCNAME, a2.SIGNSTATUS, a2.CREATEDATE, a2.SIGNEDDOCNAME, a2.SIGNEDDOCDATE FROM GOSUSLDOC.APPLICATIONS a LEFT JOIN GOSUSLDOC.APPLICATIONS_DK sdk ON a.APPID = sdk.APPID LEFT JOIN GOSUSLDOC.FLATS f ON a.APPID = f.APPID LEFT JOIN  GOSUSLDOC.APPDOCS a2 ON a.APPID = a2.APPID WHERE a.REGID = 934 AND sdk.ACTDOCNUM IN ('59-70-959001-2025-0922') ORDER BY a.PGUDATE DESC")