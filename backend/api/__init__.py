from fastapi import APIRouter
from backend.api.routes.auth import router as auth_router
from backend.api.routes.user import router as user_router
from backend.api.routes.daily_log import router as daily_log_router
from backend.api.routes.food_entry import router as food_entry_router
from backend.api.routes.food import router as food_router
from backend.api.routes.admin import router as admin_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(daily_log_router)
router.include_router(food_entry_router)
router.include_router(food_router)
router.include_router(admin_router)

