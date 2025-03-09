from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User
from backend.schemas.daily_log import DailyLogCreate, DailyLogResponse
from backend.crud.daily_log import daily_log_crud

router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

# Routes to implement:
# POST /logs - Create a new daily log
# GET /logs - Get all logs for the authenticated user
# GET /logs/{log_id} - Get details of a specific log
# PUT /logs/{log_id} - Update a log (e.g., change date)
# DELETE /logs/{log_id} - Delete a log
