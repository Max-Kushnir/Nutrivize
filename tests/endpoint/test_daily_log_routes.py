import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date, timedelta

from backend.main import app
from backend.models import DailyLog


def test_create_daily_log(authorized_client: TestClient, test_user, db_session: Session):
    """Test creating a new daily log"""
    # Don't send user_id - it should come from auth
    log_data = {}  # Empty body, will use today's date by default

    response = authorized_client.post("/api/v1/logs/", json=log_data)
    assert response.status_code == 201

    data = response.json()
    assert data["date"] == date.today().isoformat()
    assert data["user_id"] == test_user.id
    assert "id" in data

    created_log = db_session.query(DailyLog).filter(DailyLog.id == data["id"]).first()
    assert created_log is not None
    assert created_log.user_id == test_user.id


def test_create_daily_log_with_date(authorized_client: TestClient, test_user, db_session: Session):
    """Test creating a log for a specific date"""
    yesterday = date.today() - timedelta(days=1)
    log_data = {
        "date": yesterday.isoformat()
    }

    response = authorized_client.post("/api/v1/logs/", json=log_data)
    assert response.status_code == 201

    data = response.json()
    assert data["date"] == yesterday.isoformat()
    assert data["user_id"] == test_user.id


def test_create_duplicate_daily_log(authorized_client: TestClient, test_daily_log):
    """Test creating a log for a date that already has a log"""
    log_data = {
        "date": test_daily_log.date.isoformat()
    }

    response = authorized_client.post("/api/v1/logs/", json=log_data)
    assert response.status_code == 400
    assert f"Log already exists for date {test_daily_log.date}" in response.json()["detail"]


def test_create_daily_log_unauthorized(client: TestClient):
    """Test creating a log without authentication"""
    log_data = {
        "date": date.today().isoformat()
    }

    response = client.post("/api/v1/logs/", json=log_data)
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_user_logs(authorized_client: TestClient, test_user, test_daily_log, db_session: Session):
    """Test getting all logs for current user"""
    tomorrow = date.today() + timedelta(days=1)
    second_log = DailyLog(user_id=test_user.id, date=tomorrow)
    db_session.add(second_log)
    db_session.commit()

    response = authorized_client.get("/api/v1/logs/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 2

    dates = [log["date"] for log in data]
    assert test_daily_log.date.isoformat() in dates
    assert tomorrow.isoformat() in dates


def test_get_user_logs_empty(authorized_client: TestClient, test_user, db_session: Session):
    """Test getting logs when user has no logs"""
    # Delete logs for this user only
    db_session.query(DailyLog).filter(DailyLog.user_id == test_user.id).delete()
    db_session.commit()

    response = authorized_client.get("/api/v1/logs/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 0


def test_get_log_by_id(authorized_client: TestClient, test_daily_log):
    """Test getting a specific log by ID"""
    response = authorized_client.get(f"/api/v1/logs/{test_daily_log.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_daily_log.id


def test_get_nonexistent_log(authorized_client: TestClient):
    """Test getting a non-existent log"""
    response = authorized_client.get("/api/v1/logs/9999")
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_get_other_users_log(authorized_client: TestClient, db_session: Session, test_admin):
    """Test getting a log that belongs to another user"""
    admin_log = DailyLog(user_id=test_admin.id, date=date.today() - timedelta(days=1))
    db_session.add(admin_log)
    db_session.commit()

    response = authorized_client.get(f"/api/v1/logs/{admin_log.id}")
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_update_log(authorized_client: TestClient, test_daily_log, db_session: Session):
    """Test updating a log's date"""
    new_date = test_daily_log.date + timedelta(days=7)
    update_data = {
        "date": new_date.isoformat()
    }

    response = authorized_client.put(f"/api/v1/logs/{test_daily_log.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["date"] == new_date.isoformat()

    updated_log = db_session.query(DailyLog).filter(DailyLog.id == test_daily_log.id).first()
    assert updated_log.date == new_date


def test_update_nonexistent_log(authorized_client: TestClient):
    """Test updating a non-existent log"""
    update_data = {"date": date.today().isoformat()}

    response = authorized_client.put("/api/v1/logs/9999", json=update_data)
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_delete_log(authorized_client: TestClient, test_daily_log, db_session: Session):
    """Test deleting a log"""
    log_id = test_daily_log.id

    response = authorized_client.delete(f"/api/v1/logs/{log_id}")
    assert response.status_code == 204

    deleted_log = db_session.query(DailyLog).filter(DailyLog.id == log_id).first()
    assert deleted_log is None


def test_delete_nonexistent_log(authorized_client: TestClient):
    """Test deleting a non-existent log"""
    response = authorized_client.delete("/api/v1/logs/9999")
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]


def test_delete_other_users_log(authorized_client: TestClient, db_session: Session, test_admin):
    """Test deleting a log that belongs to another user"""
    admin_log = DailyLog(user_id=test_admin.id, date=date.today() - timedelta(days=2))
    db_session.add(admin_log)
    db_session.commit()

    response = authorized_client.delete(f"/api/v1/logs/{admin_log.id}")
    assert response.status_code == 404
    assert "Log not found" in response.json()["detail"]