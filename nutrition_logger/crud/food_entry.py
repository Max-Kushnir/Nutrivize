from sqlalchemy.orm import Session

from .base import CRUD

from nutrition_logger.models import DailyLog
from nutrition_logger.models import User
from nutrition_logger.models import FoodEntry

class FoodEntryCRUD(CRUD):
    def get_many_from_user(self, db: Session, user: User, limit):
        return (db.query(FoodEntry).join(DailyLog).filter(DailyLog.user_id == user.id).limit(limit).all())
    
food_entry_crud = FoodEntryCRUD(model=FoodEntry)
