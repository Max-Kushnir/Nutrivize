from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User
from backend.schemas.food import FoodCreate, FoodResponse, FoodUpdate
from backend.crud.food import food_crud

router = APIRouter(
    prefix="/foods",
    tags=["foods"]
)

# Routes to implement:
# GET /foods - List all foods
# GET /foods/{food_id} - Get details of a food item
# POST /foods - Add a new food (admin only)
# PUT /foods/{food_id} - Update food item (admin only)
# DELETE /foods/{food_id} - Remove food item (admin only)
# GET /foods/search - Search for foods by name
