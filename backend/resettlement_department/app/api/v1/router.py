from api.v1.endpoints.table import router as table_router
from api.v1.endpoints.matching import router as matching_router
from api.v1.endpoints.apartment import router as apartment_router
from api.v1.endpoints.dashboard import router as dashboard_router
from api.v1.endpoints.history import router as history_router 
from api.v1.endpoints.rsm import router as rsm_router
from api.v1.endpoints.wave import router as wave_router
from api.v1.endpoints.cin import router as cin_router 
from api.v1.endpoints.admin import router as admin_router 

from fastapi import APIRouter

router = APIRouter()

router.include_router(apartment_router)
router.include_router(table_router)
router.include_router(matching_router)
router.include_router(dashboard_router)
router.include_router(history_router)
router.include_router(rsm_router)
router.include_router(wave_router)
router.include_router(cin_router)
router.include_router(cin_router)
router.include_router(admin_router)