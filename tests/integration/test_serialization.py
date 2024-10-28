import pytest, os, datetime, json
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

from nutrition_logger.models import User, Food, DailyLog, FoodEntry
from nutrition_logger.database.db import Base
from nutrition_logger.schema.daily_log import DailyLogCreate, DailyLogResponse
from nutrition_logger.schema.user import UserCreate, UserResponse
from nutrition_logger.schema.food import FoodCreate, FoodResponse
from nutrition_logger.schema.food_entry import FoodEntryCreate, FoodEntryResponse
UserResponse.model_rebuild()

# Load environment variables
load_dotenv()

# Database configuration
user = os.environ.get("POSTGRES_USER")
password = os.environ.get("POSTGRES_PW")
db = os.environ.get("POSTGRES_TEST_DB")
host = os.environ.get("POSTGRES_HOST", "localhost")
port = os.environ.get("POSTGRES_PORT", 5432)

# Construct database URL
TEST_DB_URL = f"postgresql://{user}:{password}@{host}:{port}/{db}"

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
def test_serialize(db_session):
    user = User(username="testuser", email="testuser@example.com")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    db_user = db_session.query(User).first()
    json_user = (UserResponse.model_validate(db_user)).model_dump_json()

    parsed_json = json.loads(json_user)

    assert set(parsed_json.keys()) == {"id", "username", "email", "logs"}

    assert parsed_json["id"] == db_user.id
    assert parsed_json["username"] == db_user.username
    assert parsed_json["email"] == db_user.email
    assert parsed_json["logs"] == db_user.logs

def test_deserialize(db_session):
    user = {
        "id":1,
        "username":"testuser",
        "email":"testuser@example.com",
        "logs":[]
    }

    user_json = json.dumps(user)

    data = json.loads(user_json)
    pydantic_obj = UserCreate(**data)
    db_user = User(**pydantic_obj.model_dump())
    db_session.add(db_user)
    db_session.commit()
    db_session.refresh

    db_user = db_session.query(User).first()

    assert db_user.id == user["id"]
    assert db_user.username == user["username"]
    assert db_user.email == user["email"]
    assert db_user.logs == user["logs"]
