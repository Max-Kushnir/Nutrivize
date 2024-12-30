from __future__ import annotations
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from typing import List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .daily_log import DailyLogResponse

class UserBase(BaseModel):
    username: str = Field(min_length=1)
    email: EmailStr

class UserCreate(UserBase):
    hashed_password: str = Field(min_length=8) 

class UserResponse(UserBase):
    id: int = Field(gt=0)
    logs: List[DailyLogResponse] = []
    is_active: bool = True  

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    username: Optional[str] = Field(min_length=1)
    email: Optional[EmailStr]
    hashed_password: Optional[str] = Field(min_length=8)  

