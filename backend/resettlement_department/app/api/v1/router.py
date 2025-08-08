from api.v1.endpoints.table import router as table_router
from api.v1.endpoints.matching import router as matching_router
from api.v1.endpoints.apartment import router as apartment_router
from api.v1.endpoints.dashboard import router as dashboard_router
from api.v1.endpoints.history import router as history_router 
from api.v1.endpoints.rsm import router as rsm_router
from api.v1.endpoints.wave import router as wave_router
from api.v1.endpoints.cin import router as cin_router 
from api.v1.endpoints.admin import router as admin_router 
from api.v1.endpoints.mock_oath import router as mock_oath_router
from api.v1.endpoints.mail_index import router as mail_index_router 
from api.v1.endpoints.spd1 import router as spd1_router 
from fastapi import APIRouter

router = APIRouter()

routers = [
    apartment_router,
    table_router,
    matching_router,
    dashboard_router,
    history_router,
    rsm_router,
    wave_router,
    cin_router,
    admin_router,
    mock_oath_router, 
    mail_index_router,
    spd1_router
]

for endpoint_router in routers:
    router.include_router(endpoint_router)