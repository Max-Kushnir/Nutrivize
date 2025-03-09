from fastapi import APIRouter
from routes.auth import router as auth_router
from routes.user import router as user_router
from routes.daily_log import router as daily_log_router
from routes.food_entry import router as food_entry_router
from routes.food import router as food_router
from routes.admin import router as admin_router
from routes.nutrition import router as nutrition_router

router = APIRouter(prefix="/api/v1")

router.include_router(auth_router)
router.include_router(user_router)
router.include_router(daily_log_router)
router.include_router(food_entry_router)
router.include_router(food_router)
router.include_router(admin_router)
router.include_router(nutrition_router)
