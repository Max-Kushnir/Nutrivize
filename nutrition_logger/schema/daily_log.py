from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import List, TYPE_CHECKING

if TYPE_CHECKING:
    from .user import UserResponse
    from .food_entry import FoodEntryResponse

class DailyLogBase(BaseModel):
    user_id: int = Field(gt=0)
    
class DailyLogCreate(DailyLogBase):
    pass

class DailyLogResponse(DailyLogBase):
    id: int = Field(gt=0)
    user: UserResponse
    food_entries: List[FoodEntryResponse] = []

    model_config = ConfigDict(from_attributes=True)
