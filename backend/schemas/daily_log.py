from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, TYPE_CHECKING, Optional
from datetime import date

if TYPE_CHECKING:
    from .user import UserResponse
    from .food_entry import FoodEntryResponse

class DailyLogBase(BaseModel):
    user_id: int = Field(gt=0)
    date: Optional[date] = None
    
class DailyLogCreate(BaseModel):  # Don't inherit from Base for create
    date: Optional[date] = None  # User shouldn't send user_id
    
class DailyLogResponse(DailyLogBase):
    id: int = Field(gt=0)
    user: UserResponse
    food_entries: List[FoodEntryResponse] = []

    model_config = ConfigDict(from_attributes=True)