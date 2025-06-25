import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from backend.main import app
from backend.models import User, DailyLog, Food, FoodEntry
from backend.auth.security import get_password_hash, create_access_token
from backend.database.db import get_db

# Import test database setup from integration tests
from tests.integration.test_auth_integration import (
    engine, tables, db_session
)


@pytest.fixture
def client(db_session):
    """Return a FastAPI TestClient configured to use the test database"""
    
    def override_get_db():
        try:
            yield db_session
        finally:
            pass
    
    # Fix: Use the actual function, not a string
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides = {}


@pytest.fixture
def test_user(db_session):
    """Create a test user"""
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def test_admin(db_session):
    """Create a test admin user"""
    admin = User(
        username="adminuser",
        email="admin@example.com",
        hashed_password=get_password_hash("admin123"),
        is_active=True,
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin


@pytest.fixture
def user_token(test_user):
    """Create a token for the test user"""
    return create_access_token(data={"sub": test_user.username})


@pytest.fixture
def admin_token(test_admin):
    """Create a token for the admin user"""
    return create_access_token(data={"sub": test_admin.username})


@pytest.fixture
def authorized_client(client, user_token):
    """Return a client with a valid user token"""
    client.headers = {
        "Authorization": f"Bearer {user_token}"
    }
    return client


@pytest.fixture
def admin_client(client, admin_token):
    """Return a client with a valid admin token"""
    client.headers = {
        "Authorization": f"Bearer {admin_token}"
    }
    return client


@pytest.fixture
def test_foods(db_session):
    """Create test food items"""
    foods = [
        Food(
            name="Apple",
            calories=52,
            protein=0.3,
            carbs=14,
            fat=0.2,
            serving_size=1.0,
            unit="medium (182g)",
            manufacturer="Generic"
        ),
        Food(
            name="Chicken Breast",
            calories=165,
            protein=31,
            carbs=0,
            fat=3.6,
            serving_size=100.0,
            unit="g",
            manufacturer="Generic"
        ),
        Food(
            name="Brown Rice",
            calories=112,
            protein=2.6,
            carbs=23.5,
            fat=0.9,
            serving_size=0.5,
            unit="cup cooked (100g)",
            manufacturer="Generic"
        )
    ]
    
    for food in foods:
        db_session.add(food)
    
    db_session.commit()
    
    for food in foods:
        db_session.refresh(food)
    
    return foods


@pytest.fixture
def test_daily_log(db_session, test_user):
    """Create a test daily log"""
    daily_log = DailyLog(
        user_id=test_user.id,
        date=date.today()
    )
    db_session.add(daily_log)
    db_session.commit()
    db_session.refresh(daily_log)
    return daily_log


@pytest.fixture
def test_food_entries(db_session, test_daily_log, test_foods):
    """Create test food entries"""
    entries = [
        FoodEntry(
            daily_log_id=test_daily_log.id,  # Fixed: was log_id
            food_id=test_foods[0].id,
            quantity=1.0  # Fixed: was serving_size, removed meal_time
        ),
        FoodEntry(
            daily_log_id=test_daily_log.id,  # Fixed: was log_id
            food_id=test_foods[1].id,
            quantity=2.0  # Fixed: was serving_size, removed meal_time
        )
    ]
    for entry in entries:
        db_session.add(entry)
    db_session.commit()
    
    for entry in entries:
        db_session.refresh(entry)
    
    return entries