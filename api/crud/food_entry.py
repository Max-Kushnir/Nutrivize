from sqlalchemy.orm import Session

from .base import CRUD

from api.models import DailyLog
from api.models import User
from api.models import FoodEntry

class FoodEntryCRUD(CRUD):
    def get_many_from_user(self, db: Session, user: User, limit):
        return (db.query(FoodEntry).join(DailyLog).filter(DailyLog.user_id == user.id).limit(limit).all())
    
food_entry_crud = FoodEntryCRUD(model=FoodEntry)
