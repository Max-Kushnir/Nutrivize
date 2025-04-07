from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user
from backend.models.user import User
from backend.schemas.daily_log import DailyLogCreate, DailyLogResponse
from backend.crud.daily_log import daily_log_crud

router = APIRouter(
    prefix="/logs",
    tags=["logs"]
)

@router.post("/", response_model=DailyLogResponse, status_code=status.HTTP_201_CREATED)
async def create_daily_log(
    log: DailyLogCreate,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    """
    Create a new daily log for the authenticated user
    """
    db, current_user = db_user
    
    # Check if log already exists for this date
    existing_log = daily_log_crud.get_one(
        db, 
        daily_log_crud._model.user_id == current_user.id,
        daily_log_crud._model.date == log.date
    )
    
    if existing_log:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Log already exists for date {log.date}"
        )
    
    # Add the user_id to the log data
    log_data = log.model_dump()
    log_data["user_id"] = current_user.id
    
    # Create the log
    return daily_log_crud.create(db, log_data)

@router.get("/", response_model=List[DailyLogResponse])
async def get_user_logs(
    skip: int = 0, 
    limit: int = 100,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    """
    Get all logs for the authenticated user
    """
    db, current_user = db_user
    
    logs = daily_log_crud.get_many(
        db, 
        limit=limit, 
        user_id=current_user.id
    )
    
    return logs

@router.get("/{log_id}", response_model=DailyLogResponse)
async def get_log_by_id(
    log_id: int,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    """
    Get details of a specific log by its ID
    """
    db, current_user = db_user
    
    log = daily_log_crud.get_one(
        db, 
        daily_log_crud._model.id == log_id,
        user_id=current_user.id
    )
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    return log

@router.put("/{log_id}", response_model=DailyLogResponse)
async def update_log(
    log_id: int,
    log_update: DailyLogCreate,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    """
    Update a log's information
    """
    db, current_user = db_user
    
    # Get the existing log
    existing_log = daily_log_crud.get_one(
        db, 
        daily_log_crud._model.id == log_id,
        user_id=current_user.id
    )
    
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    # Update the log
    return daily_log_crud.update(db, existing_log, log_update)

@router.delete("/{log_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_log(
    log_id: int,
    db_user: tuple[Session, User] = Depends(get_db_user)
):
    """
    Delete a log
    """
    db, current_user = db_user
    
    # Get the existing log
    existing_log = daily_log_crud.get_one(
        db, 
        daily_log_crud._model.id == log_id,
        user_id=current_user.id
    )
    
    if not existing_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Log not found"
        )
    
    # Delete the log
    daily_log_crud.delete(db, existing_log)
    
    return None