from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

class CRUD:
    def __init__(self, model):
        self._model = model
        self._name = model.__class__.__name__
    
    def create(self, db: Session, schema):
        obj_data = schema.model_dump(exclude_none=True, exclude_unset=True)
        db_obj = self._model(**obj_data)
        db.add(db_obj)

        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Couldn't add {self._model.__name__}: {str(e)}")
        return db_obj

    def update(self, db: Session, db_obj, schema):
        obj_data = schema.model_dump(exclude_unset=True)
        for field, value in obj_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)

        try:
            db.commit()
            db.refresh(db_obj)
        except IntegrityError as e:
            db.rollback()
            raise ValueError(f"Couldn't update {self._model.__name__}: {str(e)}")
        return db_obj

    def delete(self, db: Session, db_obj):
        db.delete(db_obj)
        db.commit()
        return db_obj

    def get_one(self, db: Session, *args, **kwargs):
        return db.query(self._model).filter(*args).filter_by(**kwargs).first()
    
    def get_many(self, db: Session, limit, skip=0, *args, **kwargs):
        return db.query(self._model).filter(*args).filter_by(**kwargs).offset(skip).limit(limit).all()

    def get_many_from_user(self, db: Session, limit, id, skip=0, *args, **kwargs):
        return self.get_many(db, limit=limit, skip=skip, *args, user_id=id, **kwargs)