from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from sqlalchemy import or_

from backend.database.db import get_db
from backend.api.dependancies import get_current_active_user, get_db_user, get_db_user_admin
from backend.models.user import User
from backend.schemas.food import FoodCreate, FoodResponse, FoodUpdate
from backend.crud.food import food_crud

router = APIRouter(
    prefix="/foods",
    tags=["foods"]
)

@router.get("/", response_model=List[FoodResponse])
async def get_foods(
    skip: int = 0, 
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all foods in the database
    """
    foods = food_crud.get_many(db, limit=limit)
    return foods

@router.get("/{food_id}", response_model=FoodResponse)
async def get_food_by_id(
    food_id: int,
    db: Session = Depends(get_db)
):
    """
    Get details of a specific food item by ID
    """
    food = food_crud.get_one(db, food_crud._model.id == food_id)
    
    if not food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    return food

@router.post("/", response_model=FoodResponse, status_code=status.HTTP_201_CREATED)
async def create_food(
    food: FoodCreate,
    db_user: tuple[Session, User] = Depends(get_db_user_admin)
):
    """
    Add a new food item (admin only)
    """
    db, admin_user = db_user
    
    # Create the food
    return food_crud.create(db, food)

@router.put("/{food_id}", response_model=FoodResponse)
async def update_food(
    food_id: int,
    food_update: FoodUpdate,
    db_user: tuple[Session, User] = Depends(get_db_user_admin)
):
    """
    Update a food item (admin only)
    """
    db, admin_user = db_user
    
    # Get the existing food
    existing_food = food_crud.get_one(db, food_crud._model.id == food_id)
    
    if not existing_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    # Update the food
    return food_crud.update(db, existing_food, food_update)

@router.delete("/{food_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_food(
    food_id: int,
    db_user: tuple[Session, User] = Depends(get_db_user_admin)
):
    """
    Delete a food item (admin only)
    """
    db, admin_user = db_user
    
    # Get the existing food
    existing_food = food_crud.get_one(db, food_crud._model.id == food_id)
    
    if not existing_food:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Food not found"
        )
    
    # Delete the food
    food_crud.delete(db, existing_food)
    
    return None

@router.get("/search/", response_model=List[FoodResponse])
async def search_foods(
    query: str = Query(..., min_length=1, description="Search term"),
    limit: int = 20,
    db: Session = Depends(get_db)
):
    """
    Search for foods by name
    """
    # Create a search pattern (case insensitive)
    search_pattern = f"%{query}%"
    
    # Search for foods where name contains the search term
    foods = db.query(food_crud._model).filter(
        food_crud._model.name.ilike(search_pattern)
    ).limit(limit).all()
    
    return foods
