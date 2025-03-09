from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

# Routes to implement:
# GET /admin/stats - Get system-wide stats
# GET /admin/users-activity - Monitor user activity
# DELETE /admin/reset-database - Reset database (admin only)
