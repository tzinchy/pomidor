from fastapi import APIRouter
from api.v1.endpoints.auth import router as auth_router
from api.v1.endpoints.user import router as user_router

router = APIRouter(prefix='/v1')
router.include_router(auth_router)
router.include_router(user_router)