from fastapi import APIRouter
from depends import dashboard_service


router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


@router.get("/table")
def member():
    return dashboard_service.get_tables_data()


@router.get("/dashboard")
def dashboard():
    return dashboard_service.get_dashboard_data()


@router.get("/table/{building_id}")
def get_building_info(building_id: int):
    return dashboard_service.get_building_details(building_id)

@router.get("/house_address_with_attempt")
async def get_houes_address_with_attempt():
    return await dashboard_service.get_house_address_with_attempt()

@router.get("/district_with_attempt")
async def get_district_with_attempt():
    return await dashboard_service.get_district_with_attempt()

@router.get("/district_and_municipal_district_with_attempt")
async def get_district_and_municipal_district_with_attempt():
    return await dashboard_service.get_district_and_municipal_district_attempt()