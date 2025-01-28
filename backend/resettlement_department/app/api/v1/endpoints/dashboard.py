from fastapi import APIRouter
from depends import dashboard_service
router = APIRouter(prefix="/dashboard", tags=["Дашборд"])

@router.get("/table")
def member():
    return dashboard_service.get_tables_data()

@router.get('/dashboard')
def dashboard():
    return dashboard_service.get_dashboard_data()

@router.get("/table/{building_id}")
def get_building_info(building_id : int):
    return dashboard_service.get_building_details(building_id)