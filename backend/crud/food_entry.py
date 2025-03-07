from sqlalchemy.orm import Session

from .base import CRUD

from backend.models import DailyLog
from backend.models import User
from backend.models import FoodEntry

class FoodEntryCRUD(CRUD):
    def get_many_from_user(self, db: Session, user: User, limit):
        return (db.query(FoodEntry).join(DailyLog).filter(DailyLog.user_id == user.id).limit(limit).all())
    
food_entry_crud = FoodEntryCRUD(model=FoodEntry)
