from sqlalchemy.orm import Session

from .base import CRUD
from api.models import User

class UserCRUD(CRUD):    
    def get_by_email(self, db: Session, email: str):
        return db.query(self._model).filter(self._model.email == email).first()

user_crud = UserCRUD(model=User)
