from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from backend.database.db import get_db
from backend.api.dependancies import get_db_user_admin
from backend.models.user import User
from backend.schemas.user import UserResponse, UserUpdate
from backend.crud.user import user_crud

router = APIRouter(
    prefix="/users",
    tags=["users"]
)


@router.get("/", response_model=List[UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db_user: tuple[Session, User] = Depends(get_db_user_admin)
):
    db, admin_user = db_user
    users = user_crud.get_many(db, limit=limit, skip=skip)
    return users


@router.get("/{user_id}", response_model=UserResponse)
async def get_user_by_id(user_id: int, db_user: tuple[Session, User] = Depends(get_db_user_admin)):
    db, admin_user = db_user
    user = user_crud.get_one(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_update: UserUpdate,
    db_user: tuple[Session, User] = Depends(get_db_user_admin)
):
    db, admin_user = db_user
    existing_user = user_crud.get_one(db, id=user_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    if user_update.email and user_update.email != existing_user.email:
        email_exists = user_crud.get_by_email(db, user_update.email)
        if email_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")

    if user_update.username and user_update.username != existing_user.username:
        username_exists = user_crud.get_by_username(db, user_update.username)
        if username_exists:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already registered")

    return user_crud.update(db, existing_user, user_update)


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int, db_user: tuple[Session, User] = Depends(get_db_user_admin)):
    db, admin_user = db_user
    if user_id == admin_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete your own account"
        )
    existing_user = user_crud.get_one(db, id=user_id)
    if not existing_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    user_crud.delete(db, existing_user)
    return None
