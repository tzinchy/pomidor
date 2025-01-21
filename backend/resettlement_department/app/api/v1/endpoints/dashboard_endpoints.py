from fastapi import APIRouter
from service.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Дашборд"])

@router.get("/table")
def member():
    return DashboardService.get_tables_data()

@router.get('/dashboard')
def dashboard():
    return DashboardService.get_dashboard_data()