from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any
from datetime import datetime, timedelta

from backend.api.dependancies import get_db_user_admin
from backend.models.user import User
from backend.crud.daily_log import daily_log_crud
from backend.crud.food_entry import food_entry_crud
from backend.crud.food import food_crud

router = APIRouter(
    prefix="/admin",
    tags=["admin"]
)

@router.get("/stats", response_model=Dict[str, Any])
async def get_system_stats(db_user: tuple[Session, User] = Depends(get_db_user_admin)):
    """
    Get system-wide statistics including total users, daily logs, food entries, etc.
    Admin only endpoint.
    """
    db, current_user = db_user
    
    # Count various entities in the system
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.is_active == True).count()
    admins = db.query(User).filter(User.role == "admin").count()
    
    # Get logs from the past 30 days
    thirty_days_ago = datetime.now() - timedelta(days=30)
    recent_logs = db.query(db.query(User.id).distinct()).join(
        daily_log_crud._model, User.id == daily_log_crud._model.user_id
    ).filter(daily_log_crud._model.date >= thirty_days_ago).count()
    
    # Get total counts of different resources
    total_foods = db.query(food_crud._model).count()
    total_logs = db.query(daily_log_crud._model).count()
    total_entries = db.query(food_entry_crud._model).count()
    
    return {
        "system_stats": {
            "total_users": total_users,
            "active_users": active_users,
            "admin_users": admins,
            "users_active_last_30_days": recent_logs,
            "total_foods": total_foods,
            "total_daily_logs": total_logs,
            "total_food_entries": total_entries,
            "timestamp": datetime.now().isoformat()
        }
    }

@router.get("/users-activity")
async def get_users_activity(
    limit: int = 100,
    days: int = 7,
    db_user: tuple[Session, User] = Depends(get_db_user_admin)
):
    """
    Monitor user activity across the platform for the specified number of days.
    Admin only endpoint.
    """
    db, current_user = db_user
    
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # Get active users with their activity counts
    active_users = []
    users = db.query(User).filter(User.is_active == True).limit(limit).all()
    
    for user in users:
        # Count logs in the time period
        log_count = db.query(daily_log_crud._model).filter(
            daily_log_crud._model.user_id == user.id,
            daily_log_crud._model.date >= cutoff_date
        ).count()
        
        # Count food entries in the time period through daily logs
        entry_count = db.query(food_entry_crud._model).join(
            daily_log_crud._model, 
            food_entry_crud._model.daily_log_id == daily_log_crud._model.id
        ).filter(
            daily_log_crud._model.user_id == user.id,
            daily_log_crud._model.date >= cutoff_date
        ).count()
        
        # Only include users with some activity
        if log_count > 0 or entry_count > 0:
            active_users.append({
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "logs_count": log_count,
                "entries_count": entry_count,
                "last_login": user.last_login.isoformat() if user.last_login else None,
                "created_at": user.created_at.isoformat() if user.created_at else None
            })
    
    return {
        "time_period": f"Last {days} days",
        "total_active_users": len(active_users),
        "users": active_users,
        "timestamp": datetime.now().isoformat()
    }