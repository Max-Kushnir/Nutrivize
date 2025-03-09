from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User
from backend.schemas.user import UserResponse, UserUpdate
from backend.crud.user import user_crud

router = APIRouter(
    prefix="/users",
    tags=["users"]
)

# Routes to implement:
# GET /users - Get all users (admin only)
# GET /users/{user_id} - Get a specific user's profile (admin only)
# PUT /users/{user_id} - Update user profile (admin only)
# DELETE /users/{user_id} - Delete a user (admin only)
