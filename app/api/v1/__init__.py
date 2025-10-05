from fastapi import APIRouter

from app.routers.bill import router as bills_router
from app.routers.user import router as users_router

api_router = APIRouter(
    prefix="/api/v1"
)
api_router.include_router(bills_router)
api_router.include_router(users_router)
