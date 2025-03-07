from sqlalchemy.orm import Session

from .base import CRUD
from backend.models import User

class UserCRUD(CRUD):    
    def get_by_email(self, db: Session, email: str):
        return db.query(self._model).filter(self._model.email == email).first()
    
    def get_by_username(self, db: Session, username: str):
        return db.query(self._model).filter(self._model.username == username).first()

user_crud = UserCRUD(model=User)
