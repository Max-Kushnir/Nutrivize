import pytest, os, datetime, json
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from backend.models import User, Food, DailyLog, FoodEntry
from backend.database.db import Base
from backend.schemas.daily_log import DailyLogCreate, DailyLogResponse
from backend.schemas.user import UserCreate, UserResponse
from backend.schemas.food import FoodCreate, FoodResponse
from backend.schemas.food_entry import FoodEntryCreate, FoodEntryResponse
from backend.config import settings

UserResponse.model_rebuild()

# Database configuration
TEST_DB_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_TEST_DB}"
)

# connect to database
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL, echo=True)
    yield engine

# construct engine
@pytest.fixture(scope="function")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

# create session
@pytest.fixture(scope="function")
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# testing serialization and deserialization with sqlalchemy
def test_deserialize(db_session):
    user = {
        "id": 1,
        "username": "testuser",
        "email": "testuser@example.com",
        "logs": [],
        "hashed_password": "hashed_password_placeholder"  
    }
    user_json = json.dumps(user)
    data = json.loads(user_json)
    
    pydantic_obj = UserCreate(**data)
    db_user = User(**pydantic_obj.model_dump())
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    db_user = db_session.query(User).first()

    assert db_user.id == user["id"]
    assert db_user.username == user["username"]
    assert db_user.email == user["email"]
    assert db_user.logs == user["logs"]
    assert db_user.hashed_password == user["hashed_password"]

def test_deserialize(db_session):
    user = {
        "id":1,
        "username":"testuser",
        "email":"testuser@example.com",
        "logs":[]
    }

    user_json = json.dumps(user)

    data = json.loads(user_json)
    pydantic_obj = UserCreate(**data, hashed_password="hashed_password_placeholder")
    db_user = User(**pydantic_obj.model_dump())
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh(db_user)

    db_user = db_session.query(User).first()

    assert db_user.id == user["id"]
    assert db_user.username == user["username"]
    assert db_user.email == user["email"]
    assert db_user.logs == user["logs"]