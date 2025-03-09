from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User
from backend.schema.food_entry import FoodEntryCreate, FoodEntryResponse, FoodEntryUpdate
from backend.crud.food_entry import food_entry_crud
from backend.crud.daily_log import daily_log_crud

router = APIRouter(
    prefix="/logs/{log_id}/entries",
    tags=["food entries"]
)

# Routes to implement:
# POST /logs/{log_id}/entries - Add food to a daily log
# GET /logs/{log_id}/entries - List all food entries for a log
# GET /logs/{log_id}/entries/{entry_id} - Get details of a specific entry
# PUT /logs/{log_id}/entries/{entry_id} - Update entry (portion size, food item)
# DELETE /logs/{log_id}/entries/{entry_id} - Remove a food entry
