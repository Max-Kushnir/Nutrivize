from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.models.user import User
from backend.auth.auth import get_current_user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Get current user and verify they're active
    """
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

def get_db_user(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> tuple[Session, User]:
    """
    Common dependency that provides both database session and current user.
    Used for endpoints that need both db access and user authentication.
    """
    return db, current_user

def get_db_user_admin(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
) -> tuple[Session, User]:
    """
    Common dependency that provides both database session and current user.
    Used for endpoints that need both db access and user authentication.
    """
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    return db, current_user