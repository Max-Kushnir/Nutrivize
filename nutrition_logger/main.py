import json, uvicorn
from fastapi import FastAPI

from nutrition_logger.database.db import get_db
from nutrition_logger.models import User, DailyLog, Food, FoodEntry
from nutrition_logger.schema import (
    UserCreate, UserResponse, UserUpdate,
    FoodCreate, FoodResponse, FoodUpdate, 
    DailyLogCreate, DailyLogResponse, 
    FoodEntryCreate, FoodEntryResponse, FoodEntryUpdate
)

db = get_db()
app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

if __name__ == "__main__":
    uvicorn.run("nutrition_logger.main:app", port=5000, log_level="info")