from fastapi import APIRouter
from depends import dashboard_service
from fastapi_cache.decorator import cache
import asyncio

router = APIRouter(prefix="/dashboard", tags=["Дашборд"])

@router.get("/data")
@cache(expire=60)
async def get_data():
    
    return {"message": "Этот ответ закэширован в RAM!"}


@router.get("/table")
@cache(expire=60)
def member():
    return dashboard_service.get_tables_data()

@router.get('/dashboard')
@cache(expire=60)
def dashboard():
    return dashboard_service.get_dashboard_data()