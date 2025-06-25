from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.db import get_db
from backend.api.dependancies import get_db_user
from backend.models.user import User
from backend.schemas.food_entry import FoodEntryCreate, FoodEntryResponse, FoodEntryUpdate
from backend.crud.food_entry import food_entry_crud
from backend.crud.daily_log import daily_log_crud
from backend.crud.food import food_crud

router = APIRouter(
    prefix="/logs/{daily_log_id}/entries",
    tags=["food entries"]
)


@router.post("/", response_model=FoodEntryResponse, status_code=status.HTTP_201_CREATED)
async def create_food_entry(
    daily_log_id: int,
    entry: FoodEntryCreate,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    db, current_user = db_user

    log = daily_log_crud.get_one(db, daily_log_crud._model.id == daily_log_id, user_id=current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    food = food_crud.get_one(db, food_crud._model.id == entry.food_id)
    if not food:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    entry_data = entry.model_dump()
    entry_data["daily_log_id"] = daily_log_id
    return food_entry_crud.create(db, entry_data)


@router.get("/", response_model=List[FoodEntryResponse])
async def get_food_entries(daily_log_id: int, db_user: tuple[Session, User] = Depends(get_db_user)):
    db, current_user = db_user

    log = daily_log_crud.get_one(db, daily_log_crud._model.id == daily_log_id, user_id=current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    entries = food_entry_crud.get_many(db, limit=1000, daily_log_id=daily_log_id)
    return entries


@router.get("/{entry_id}", response_model=FoodEntryResponse)
async def get_food_entry(daily_log_id: int, entry_id: int, db_user: tuple[Session, User] = Depends(get_db_user)):
    db, current_user = db_user
    log = daily_log_crud.get_one(db, daily_log_crud._model.id == daily_log_id, user_id=current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    entry = food_entry_crud.get_one(db, food_entry_crud._model.id == entry_id, daily_log_id=daily_log_id)
    if not entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food entry not found")
    return entry


@router.put("/{entry_id}", response_model=FoodEntryResponse)
async def update_food_entry(
    daily_log_id: int,
    entry_id: int,
    entry_update: FoodEntryUpdate,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    db, current_user = db_user

    log = daily_log_crud.get_one(db, daily_log_crud._model.id == daily_log_id, user_id=current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    existing_entry = food_entry_crud.get_one(db, food_entry_crud._model.id == entry_id, daily_log_id=daily_log_id)
    if not existing_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food entry not found")

    if entry_update.food_id and entry_update.food_id != existing_entry.food_id:
        food = food_crud.get_one(db, food_crud._model.id == entry_update.food_id)
        if not food:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food not found")

    return food_entry_crud.update(db, existing_entry, entry_update)


@router.delete("/{entry_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food_entry(
    daily_log_id: int,
    entry_id: int,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    db, current_user = db_user

    log = daily_log_crud.get_one(db, daily_log_crud._model.id == daily_log_id, user_id=current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    existing_entry = food_entry_crud.get_one(db, food_entry_crud._model.id == entry_id, daily_log_id=daily_log_id)
    if not existing_entry:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Food entry not found")

    food_entry_crud.delete(db, existing_entry)
    return None
