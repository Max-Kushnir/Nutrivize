from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from backend.crud.base import CRUD
from backend.models.user import User
from backend.schemas.user import UserCreate
from backend.auth.security import get_password_hash

class UserCRUD(CRUD):
    def __init__(self):
        super().__init__(User)

    def get_by_email(self, db: Session, email: str):
        return db.query(self._model).filter(self._model.email == email).first()
    
    def get_by_username(self, db: Session, username: str):
        return db.query(self._model).filter(self._model.username == username).first()
    
    @staticmethod
    def deactivate_user(self, db: Session, user: User):
        user.is_active = False
        db.add(user)
        db.commit()
        return user
    
user_crud = UserCRUD(model=User)
