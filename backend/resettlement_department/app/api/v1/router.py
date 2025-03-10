from api.v1.endpoints.apartment import router as apartment_router
from api.v1.endpoints.matching import router as matching_router
#from api.v1.endpoints.load import router as load_router
from api.v1.endpoints.dashboard import router as dashboard_router
from api.v1.endpoints.history import router as history_router 
from api.v1.endpoints.rsm import router as rsm_router

from fastapi import APIRouter

router = APIRouter()

router.include_router(apartment_router)
router.include_router(matching_router)
router.include_router(dashboard_router)
router.include_router(history_router)
router.include_router(rsm_router)
