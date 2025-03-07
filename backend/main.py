import json, uvicorn
from fastapi import FastAPI

from backend.database.db import get_db
from backend.models import User, DailyLog, Food, FoodEntry
from backend.schema import (
    UserBase, UserCreate, UserResponse,
    FoodBase, FoodCreate, FoodResponse, 
    DailyLogBase, DailyLogCreate, DailyLogResponse, 
    FoodEntryBase, FoodEntryCreate, FoodEntryResponse
)

db = get_db()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("api.main:app", port=5000, log_level="info")