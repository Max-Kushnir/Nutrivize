from pydantic import BaseModel, Field, ConfigDict
from typing import Optional

class FoodBase(BaseModel):
    name: str = Field(min_length=1)
    manufacturer: str = Field(min_length=1)
    serving_size: float = Field(gt=0, default=1.0)
    unit: str = Field(min_length=1)
    calories: float = Field(ge=0, default=0)
    protein: float = Field(ge=0, default=0)
    carbs: float = Field(ge=0, default=0)
    fat: float = Field(ge=0, default=0)

class FoodCreate(FoodBase):
    pass

class FoodResponse(FoodBase):
    id: int = Field(gt=0)
    
    model_config = ConfigDict(from_attributes=True)

class FoodUpdate(BaseModel):
    name: Optional[str] = Field(min_length=1)
    manufacturer: Optional[str] = Field(min_length=1)
    serving_size: Optional[float] = Field(gt=0, default=1.0)
    unit: Optional[str] = Field(min_length=1)
    calories: Optional[float] = Field(ge=0, default=0)
    protein: Optional[float] = Field(ge=0, default=0)
    carbs: Optional[float] = Field(ge=0, default=0)
    fat: Optional[float] = Field(ge=0, default=0)