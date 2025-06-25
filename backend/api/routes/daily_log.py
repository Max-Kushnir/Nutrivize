from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import date

from backend.database.db import get_db
from backend.api.dependancies import get_db_user
from backend.models.user import User
from backend.schemas.daily_log import DailyLogCreate, DailyLogResponse
from backend.crud.daily_log import daily_log_crud

router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

@router.post("/", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_log(log: DailyLogCreate, db_user: tuple[Session, User] = Depends(get_db_user)):
    db, current_user = db_user

    # Use the date from request or default to today
    log_date = log.date if log.date else date.today()
    
    existing_log = daily_log_crud.get_one(
        db,
        daily_log_crud._model.user_id == current_user.id,
        daily_log_crud._model.date == log_date  # Use log_date instead of log.date
    )
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Log already exists for date {log_date}"
        )

    log_data = log.model_dump(exclude={'user_id'})  # Exclude user_id from request
    log_data["user_id"] = current_user.id  # Always use current user's ID
    log_data["date"] = log_date  # Explicitly set the date
    return daily_log_crud.create(db, log_data)

@router.get("/", response_model=List[DailyLogResponse])
async def get_user_logs(skip: int = 0, limit: int = 100, db_user: tuple[Session, User] = Depends(get_db_user)):
    db, current_user = db_user
    logs = daily_log_crud.get_many(db, limit=limit, skip=skip, user_id=current_user.id)
    return logs


@router.get("/{log_id}", response_model=DailyLogResponse)
async def get_log_by_id(log_id: int, db_user: tuple[Session, User] = Depends(get_db_user)):
    db, current_user = db_user
    log = daily_log_crud.get_one(db, daily_log_crud._model.id == log_id, user_id=current_user.id)
    if not log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")
    return log


@router.put("/{log_id}", response_model=DailyLogResponse)
async def update_log(
    log_id: int,
    log_update: DailyLogCreate,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    db, current_user = db_user
    existing_log = daily_log_crud.get_one(db, daily_log_crud._model.id == log_id, user_id=current_user.id)
    if not existing_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    return daily_log_crud.update(db, existing_log, log_update)


@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(log_id: int, db_user: tuple[Session, User] = Depends(get_db_user)):
    db, current_user = db_user
    existing_log = daily_log_crud.get_one(db, daily_log_crud._model.id == log_id, user_id=current_user.id)
    if not existing_log:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Log not found")

    daily_log_crud.delete(db, existing_log)
    return None
