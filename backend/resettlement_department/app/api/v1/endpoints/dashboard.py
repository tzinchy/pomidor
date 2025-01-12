from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from service.dashboard_service import DashboardService

router = APIRouter(prefix="/dashboard", tags=["Первичный подбор"])


@router.get("/react/{params}")
async def table_page(params: str):
    """
    Перенаправляет запрос на указанный адрес с переданными параметрами.
    """
    print(params)
    redirect_url = f"http://10.9.96.160:3000/{params}"
    return RedirectResponse(redirect_url)


@router.get("/members")
async def member():
    return await DashboardService.get_dashboard_data()