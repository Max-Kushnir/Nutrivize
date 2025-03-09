from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Optional

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User

router = APIRouter(
    prefix="/nutrition",
    tags=["nutrition"]
)

# Routes to implement:
# GET /nutrition/summary - Get user nutrition summary
# GET /nutrition/goals - Get user's nutrition goals
# PUT /nutrition/goals - Set/update nutrition goals