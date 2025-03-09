import pytest
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session

from backend.database.db import Base
from backend.crud import user_crud, food_crud, daily_log_crud, food_entry_crud
from backend.schemas.user import UserCreate
from backend.schemas.food import FoodCreate
from backend.schemas.daily_log import DailyLogCreate
from backend.schemas.food_entry import FoodEntryCreate
from backend.config import settings

# Database configuration
TEST_DB_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_TEST_DB}"
)

# Fixtures
@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DB_URL, echo=True)
    yield engine

@pytest.fixture(scope="function")
def tables(engine):
    Base.metadata.create_all(engine)
    yield
    Base.metadata.drop_all(engine)

@pytest.fixture(scope="function")
def db_session(engine, tables):
    connection = engine.connect()
    transaction = connection.begin()
    Session = sessionmaker(bind=connection)
    session = Session()
    
    try:
        yield session
    finally:
        session.close()
        # Only rollback if the transaction is still active
        if transaction.is_active:
            transaction.rollback()
        connection.close()

# Smoke tests
def test_database_connection(engine):
    with engine.connect() as conn:
        assert conn is not None

def test_tables_exist(engine, tables):
    inspector = inspect(engine)
    existing_tables = inspector.get_table_names()
    expected_tables = ['users', 'foods', 'daily_logs', 'food_entries']
    assert set(expected_tables).issubset(set(existing_tables))

def test_session_exists(db_session):
    assert db_session.is_active
    assert isinstance(db_session, Session)
    assert db_session.bind is not None

# User CRUD Tests
def test_user_crud_create(db_session):
    user_schema = UserCreate(username="testuser", email="test@example.com", hashed_password="hashed_password_placeholder")
    user = user_crud.create(db_session, user_schema)
    assert user.username == "testuser"
    assert user.email == "test@example.com"

def test_user_crud_create_duplicate_username(db_session):
    # Create first user
    user_schema = UserCreate(username="testuser", email="test1@example.com", hashed_password="hashed_password_placeholder")
    user_crud.create(db_session, user_schema)
    
    # Attempt to create user with same username
    duplicate_schema = UserCreate(username="testuser", email="test2@example.com", hashed_password="hashed_password_placeholder")
    with pytest.raises(ValueError) as exc:
        user_crud.create(db_session, duplicate_schema)
    assert "username" in str(exc.value).lower()

def test_user_crud_create_duplicate_email(db_session):
    # Create first user
    user_schema = UserCreate(username="testuser1", email="test@example.com", hashed_password="hashed_password_placeholder")
    user_crud.create(db_session, user_schema)
    
    # Attempt to create user with same email
    duplicate_schema = UserCreate(username="testuser2", email="test@example.com", hashed_password="hashed_password_placeholder")
    with pytest.raises(ValueError) as exc:
        user_crud.create(db_session, duplicate_schema)
    assert "email" in str(exc.value).lower()

def test_user_crud_update_to_existing_username(db_session):
    # Create two users
    user1 = user_crud.create(db_session, UserCreate(username="user1", email="user1@example.com", hashed_password="hashed_password_placeholder"))
    user_crud.create(db_session, UserCreate(username="user2", email="user2@example.com", hashed_password="hashed_password_placeholder"))
    
    # Try to update first user to have second user's username
    update_schema = UserCreate(username="user2", email="user1@example.com", hashed_password="hashed_password_placeholder")
    with pytest.raises(ValueError) as exc:
        user_crud.update(db_session, user1, update_schema)
    assert "username" in str(exc.value).lower()

# Food CRUD Tests
def test_food_crud_create_duplicate_name_same_manufacturer(db_session):
    # Create first food
    food_schema = FoodCreate(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    food_crud.create(db_session, food_schema)
    
    # Attempt to create duplicate food
    with pytest.raises(ValueError) as exc:
        food_crud.create(db_session, food_schema)
    assert "food" in str(exc.value).lower()

def test_food_crud_create_same_name_different_manufacturer(db_session):
    # Create first food
    food1_schema = FoodCreate(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    food_crud.create(db_session, food1_schema)
    
    # Create food with same name but different manufacturer
    food2_schema = FoodCreate(
        name="Banana",
        manufacturer="Dole",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    food2 = food_crud.create(db_session, food2_schema)
    assert food2 is not None
    assert food2.manufacturer == "Dole"

def test_food_crud_create_duplicate_name_manufacturer(db_session):
    # Create first banana from Walmart
    food1_schema = FoodCreate(
        name="Banana",
        manufacturer="Walmart",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    food1 = food_crud.create(db_session, food1_schema)
    assert food1 is not None

    # Create banana from Target - should succeed
    food2_schema = FoodCreate(
        name="Banana",
        manufacturer="Target",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    food2 = food_crud.create(db_session, food2_schema)
    assert food2 is not None

    # Try to create another banana from Walmart - should fail
    food3_schema = FoodCreate(
        name="Banana",
        manufacturer="Walmart",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    with pytest.raises(ValueError) as exc:
        food_crud.create(db_session, food3_schema)
    assert "name" in str(exc.value).lower() and "manufacturer" in str(exc.value).lower()

# Daily Log CRUD Tests
def test_daily_log_crud_create(db_session):
    # Create a user first
    user_schema = UserCreate(username="testuser", email="test@example.com", hashed_password="hashed_password_placeholder")
    user = user_crud.create(db_session, user_schema)
    
    log_schema = DailyLogCreate(user_id=user.id)
    log = daily_log_crud.create(db_session, log_schema)
    
    assert log.user_id == user.id
    assert log.date is not None  # Date should be automatically set

def test_daily_log_crud_create_duplicate_date(db_session):
    # Create a user first
    user_schema = UserCreate(username="testuser", email="test@example.com", hashed_password="hashed_password_placeholder")
    user = user_crud.create(db_session, user_schema)
    
    # Create first log
    log_schema = DailyLogCreate(user_id=user.id)
    daily_log_crud.create(db_session, log_schema)
    
    # Attempt to create second log for same date should raise ValueError
    with pytest.raises(ValueError):
        daily_log_crud.create(db_session, log_schema)

def test_daily_log_crud_get_many_from_user(db_session):
    # Create a user first
    user_schema = UserCreate(username="testuser", email="test@example.com", hashed_password="hashed_password_placeholder")
    user = user_crud.create(db_session, user_schema)
    
    # Create a log
    log_schema = DailyLogCreate(user_id=user.id)
    log = daily_log_crud.create(db_session, log_schema)
    
    logs = daily_log_crud.get_many_from_user(db_session, limit=5, id=user.id)
    assert len(logs) == 1
    assert all(log.user_id == user.id for log in logs)

def test_daily_log_crud_create_invalid_user_id(db_session):
    # Attempt to create log with non-existent user_id
    log_schema = DailyLogCreate(user_id=999)
    with pytest.raises(ValueError) as exc:
        daily_log_crud.create(db_session, log_schema)
    assert "user" in str(exc.value).lower()

# Food Entry CRUD Tests
def test_food_entry_crud_create_invalid_log_id(db_session):
    # Create food but use invalid log_id
    food_schema = FoodCreate(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    food = food_crud.create(db_session, food_schema)
    
    entry_schema = FoodEntryCreate(daily_log_id=999, food_id=food.id)
    with pytest.raises(ValueError) as exc:
        food_entry_crud.create(db_session, entry_schema)
    assert "log" in str(exc.value).lower()

def test_food_entry_crud_create_invalid_food_id(db_session):
    # Create user and log but use invalid food_id
    user = user_crud.create(db_session, UserCreate(username="testuser", email="test@example.com", hashed_password="hashed_password_placeholder"))
    log = daily_log_crud.create(db_session, DailyLogCreate(user_id=user.id))
    
    entry_schema = FoodEntryCreate(daily_log_id=log.id, food_id=999)
    with pytest.raises(ValueError) as exc:
        food_entry_crud.create(db_session, entry_schema)
    assert "food" in str(exc.value).lower()
