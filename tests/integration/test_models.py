import pytest, os, datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session

from api.models import User, Food, DailyLog, FoodEntry
from api.database.db import Base
from api.config import settings

# Database configuration
TEST_DB_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_DB}"
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

# smoke tests to check that sqlalchemy and database are properly set up
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

# testing sqlalchemy class functionality with postgres database
def test_add_user(db_session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    added_user = db_session.query(User).filter_by(username="testuser").first()

    assert added_user is not None
    assert added_user.id == 1
    assert added_user.username == "testuser"
    assert added_user.email == "testuser@example.com"

def test_add_food(db_session):
    food = Food(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    added_food = db_session.query(Food).filter_by(name="Banana").first()

    assert added_food is not None
    assert added_food.name == "Banana"
    assert added_food.manufacturer == "Chiquita"
    assert added_food.serving_size == 118
    assert added_food.unit== "g"
    assert added_food.calories == 105
    assert added_food.protein == 1.3
    assert added_food.carbs == 27
    assert added_food.fat == 0.3

def test_add_log(db_session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    log = DailyLog(user_id=1) 
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    added_log = db_session.query(DailyLog).filter_by(user_id=1).first()

    assert added_log.user_id == 1

def test_add_food_entry(db_session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    food = Food(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    log = DailyLog(user_id=1) 
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    food_entry = FoodEntry(daily_log_id=1, food_id=1)
    db_session.add(food_entry)
    db_session.commit()
    db_session.refresh(food_entry)

    added_food_entry = db_session.query(FoodEntry).filter_by(daily_log_id=1).first()

    assert added_food_entry.daily_log_id == 1
    assert added_food_entry.quantity == 1.0
    assert added_food_entry.food.name == "Banana"
    assert added_food_entry.daily_log.user.username == "testuser"

def test_update_user(db_session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    user = db_session.query(User).filter_by(username="testuser").first()
    assert user is not None

    user.email = "updated_testuser@example.com"
    db_session.commit()
    db_session.refresh(user)

    updated_user = db_session.query(User).filter_by(username="testuser").first()

    assert updated_user is not None
    assert updated_user.email == "updated_testuser@example.com"

def test_update_food(db_session):
    food = Food(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    food = db_session.query(Food).filter_by(name="Banana").first()
    assert food is not None

    food.manufacturer = "Updated Manufacturer"
    food.calories = 110
    db_session.commit()
    db_session.refresh(food)

    updated_food = db_session.query(Food).filter_by(name="Banana").first()

    assert updated_food is not None
    assert updated_food.manufacturer == "Updated Manufacturer"
    assert updated_food.calories == 110

def test_update_daily_log(db_session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    log = DailyLog(user_id=1) 
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    user = db_session.query(User).filter_by(username="testuser").first()
    assert user is not None

    log = db_session.query(DailyLog).filter_by(user_id=user.id).first()
    assert log is not None

    original_date = log.date
    new_date = original_date + datetime.timedelta(days=1)
    log.date = new_date
    db_session.commit()
    db_session.refresh(log)

    updated_log = db_session.query(DailyLog).filter_by(user_id=user.id, date=new_date).first()

    assert updated_log is not None
    assert updated_log.date == new_date

def test_update_food_entry(db_session):
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    food = Food(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    log = DailyLog(user_id=1) 
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    food_entry = FoodEntry(daily_log_id=1, food_id=1)
    db_session.add(food_entry)
    db_session.commit()
    db_session.refresh(food_entry)

    user = db_session.query(User).filter_by(username="testuser").first()
    assert user is not None

    log = db_session.query(DailyLog).filter_by(user_id=user.id).first()
    assert log is not None

    food = db_session.query(Food).filter_by(name="Banana").first()
    assert food is not None

    food_entry = db_session.query(FoodEntry).filter_by(daily_log_id=log.id, food_id=food.id).first()
    assert food_entry is not None

    original_quantity = food_entry.quantity
    food_entry.quantity = original_quantity + 1.0
    db_session.commit()
    db_session.refresh(food_entry)

    updated_food_entry = db_session.query(FoodEntry).filter_by(daily_log_id=log.id, food_id=food.id).first()

    assert updated_food_entry is not None
    assert updated_food_entry.quantity == original_quantity + 1.0

# children of user and list should be deleted if their parent is removed from database
def test_cascade_delete(db_session): 
    user = User(username="testuser", email="testuser@example.com", hashed_password="hashed_password_placeholder")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    food = Food(
        name="Banana",
        manufacturer="Chiquita",
        serving_size=118,
        unit="g",
        calories=105,
        protein=1.3,
        carbs=27,
        fat=0.3
    )
    db_session.add(food)
    db_session.commit()
    db_session.refresh(food)

    log = DailyLog(user_id=1) 
    db_session.add(log)
    db_session.commit()
    db_session.refresh(log)

    food_entry = FoodEntry(daily_log_id=1, food_id=1)
    db_session.add(food_entry)
    db_session.commit()
    db_session.refresh(food_entry)

    added_user = db_session.query(User).filter_by(username="testuser").first()
    db_session.delete(added_user)
    db_session.commit()
    
    added_user = db_session.query(User).filter_by(username="testuser").first()
    added_log = db_session.query(DailyLog).filter_by(user_id=1).first()
    added_food_entry = db_session.query(FoodEntry).filter_by(daily_log_id=1).first()
    
    assert added_user == None
    assert added_log == None
    assert added_food_entry == None
