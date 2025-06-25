import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models import FoodEntry, DailyLog


def test_create_food_entry(authorized_client: TestClient, test_daily_log, test_foods, db_session: Session):
    """Test creating a new food entry"""
    entry_data = {
        "food_id": test_foods[0].id,
        "serving_size": 1.5,
        "meal_time": "breakfast"
    }

    response = authorized_client.post(f"/api/v1/logs/{test_daily_log.id}/entries/", json=entry_data)
    assert response.status_code == 201

    data = response.json()
    assert data["food_id"] == entry_data["food_id"]
    assert data["serving_size"] == entry_data["serving_size"]
    assert data["meal_time"] == entry_data["meal_time"]
    assert data["log_id"] == test_daily_log.id
    assert "id" in data

    created_entry = db_session.query(FoodEntry).filter(FoodEntry.id == data["id"]).first()
    assert created_entry is not None
    assert created_entry.food_id == entry_data["food_id"]


def test_create_food_entry_nonexistent_log(authorized_client: TestClient, test_foods):
    """Test creating a food entry for a non-existent log"""
    entry_data = {
        "food_id": test_foods[0].id,
        "serving_size": 1.0,
        "meal_time": "breakfast"
    }

    response = authorized_client.post("/api/v1/logs/9999/entries/", json=entry_data)
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_create_food_entry_nonexistent_food(authorized_client: TestClient, test_daily_log):
    """Test creating a food entry with a non-existent food"""
    entry_data = {
        "food_id": 9999,
        "serving_size": 1.0,
        "meal_time": "breakfast"
    }

    response = authorized_client.post(f"/api/v1/logs/{test_daily_log.id}/entries/", json=entry_data)
    assert response.status_code == 404
    assert "Food not found" in response.json()["detail"]


def test_create_food_entry_other_users_log(authorized_client: TestClient, db_session: Session, test_admin, test_foods):
    """Test creating a food entry for another user's log"""
    admin_log = DailyLog(user_id=test_admin.id, date="2023-01-01")
    db_session.add(admin_log)
    db_session.commit()
    db_session.refresh(admin_log)

    entry_data = {
        "food_id": test_foods[0].id,
        "serving_size": 1.0,
        "meal_time": "breakfast"
    }

    response = authorized_client.post(f"/api/v1/logs/{admin_log.id}/entries/", json=entry_data)
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_get_food_entries(authorized_client: TestClient, test_daily_log, test_foods, test_food_entries):
    """Test getting all food entries for a log"""
    response = authorized_client.get(f"/api/v1/logs/{test_daily_log.id}/entries/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == len(test_food_entries)

    entry_ids = [entry["id"] for entry in data]
    expected_ids = [entry.id for entry in test_food_entries]

    for eid in expected_ids:
        assert eid in entry_ids


def test_get_food_entries_empty(authorized_client: TestClient, db_session: Session, test_user):
    """Test getting entries for a log with no entries"""
    empty_log = DailyLog(user_id=test_user.id, date="2023-01-02")
    db_session.add(empty_log)
    db_session.commit()
    db_session.refresh(empty_log)

    response = authorized_client.get(f"/api/v1/logs/{empty_log.id}/entries/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_food_entries_nonexistent_log(authorized_client: TestClient):
    """Test getting entries for a non-existent log"""
    response = authorized_client.get("/api/v1/logs/9999/entries/")
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_get_food_entry_by_id(authorized_client: TestClient, test_daily_log, test_food_entries):
    """Test getting a specific food entry by ID"""
    entry_id = test_food_entries[0].id

    response = authorized_client.get(f"/api/v1/logs/{test_daily_log.id}/entries/{entry_id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == entry_id
    assert data["log_id"] == test_daily_log.id


def test_get_nonexistent_food_entry(authorized_client: TestClient, test_daily_log):
    """Test getting a non-existent food entry"""
    response = authorized_client.get(f"/api/v1/logs/{test_daily_log.id}/entries/9999")
    assert response.status_code == 404
    assert "Food entry not found" in response.json()["detail"]


def test_get_food_entry_wrong_log(authorized_client: TestClient, test_daily_log, db_session: Session, test_user, test_foods):
    """Test getting a food entry with the wrong log ID"""
    from backend.models import FoodEntry
    second_log = DailyLog(user_id=test_user.id, date="2023-01-02")
    db_session.add(second_log)
    db_session.commit()
    db_session.refresh(second_log)

    entry = FoodEntry(log_id=second_log.id, food_id=test_foods[0].id, serving_size=1.0)
    db_session.add(entry)
    db_session.commit()
    db_session.refresh(entry)

    response = authorized_client.get(f"/api/v1/logs/{test_daily_log.id}/entries/{entry.id}")
    assert response.status_code == 404
    assert "Food entry not found" in response.json()["detail"]


def test_update_food_entry(authorized_client: TestClient, test_daily_log, test_food_entries, test_foods, db_session: Session):
    """Test updating a food entry"""
    entry_id = test_food_entries[0].id
    update_data = {
        "food_id": test_foods[1].id,
        "serving_size": 2.0,
        "meal_time": "dinner"
    }

    response = authorized_client.put(f"/api/v1/logs/{test_daily_log.id}/entries/{entry_id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == entry_id
    assert data["food_id"] == update_data["food_id"]
    assert data["serving_size"] == update_data["serving_size"]
    assert data["meal_time"] == update_data["meal_time"]

    updated_entry = db_session.query(FoodEntry).filter(FoodEntry.id == entry_id).first()
    assert updated_entry.food_id == update_data["food_id"]


def test_update_food_entry_nonexistent_food(authorized_client: TestClient, test_daily_log, test_food_entries):
    """Test updating a food entry with a non-existent food"""
    entry_id = test_food_entries[0].id
    update_data = {
        "food_id": 9999,
        "serving_size": 1.0
    }

    response = authorized_client.put(f"/api/v1/logs/{test_daily_log.id}/entries/{entry_id}", json=update_data)
    assert response.status_code == 404
    assert "Food not found" in response.json()["detail"]


def test_delete_food_entry(authorized_client: TestClient, test_daily_log, test_food_entries, db_session: Session):
    """Test deleting a food entry"""
    entry_id = test_food_entries[0].id

    response = authorized_client.delete(f"/api/v1/logs/{test_daily_log.id}/entries/{entry_id}")
    assert response.status_code == 204

    deleted_entry = db_session.query(FoodEntry).filter(FoodEntry.id == entry_id).first()
    assert deleted_entry is None


def test_delete_nonexistent_food_entry(authorized_client: TestClient, test_daily_log):
    """Test deleting a non-existent food entry"""
    response = authorized_client.delete(f"/api/v1/logs/{test_daily_log.id}/entries/9999")
    assert response.status_code == 404
    assert "Food entry not found" in response.json()["detail"]
