from __future__ import annotations
from pydantic import BaseModel, Field, ConfigDict
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .daily_log import DailyLogResponse
    from .food import FoodResponse

class FoodEntryBase(BaseModel):
    daily_log_id: int = Field(gt=0)
    food_id: int = Field(gt=0)
    quantity: float = Field(gt=0, default=1)
     
class FoodEntryCreate(FoodEntryBase):
    pass

class FoodEntryResponse(BaseModel):
    id: int = Field(gt=0)
    log_id: int = Field(gt=0, alias="daily_log_id")  # Use alias
    food_id: int = Field(gt=0)
    quantity: float = Field(gt=0)
    food: FoodResponse

    model_config = ConfigDict(
        from_attributes=True,
        populate_by_name=True  # Allow both log_id and daily_log_id
    )


class FoodEntryUpdate(BaseModel):
    quantity: Optional[float] = Field(gt=0)