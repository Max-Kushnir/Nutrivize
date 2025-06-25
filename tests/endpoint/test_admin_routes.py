import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import date

from backend.main import app
from backend.models import User, DailyLog, Food, FoodEntry


def test_get_stats_admin(admin_client: TestClient, test_user, test_admin,
                         test_foods, test_daily_log, test_food_entries):
    """Test getting system stats as admin"""
    response = admin_client.get("/api/v1/admin/stats")
    assert response.status_code == 200

    data = response.json()

    # Check that response contains required sections
    assert "system_stats" in data
    stats = data["system_stats"]

    # Basic checks
    assert stats["total_users"] >= 2  # At least test_user and test_admin
    assert stats["active_users"] >= 2
    assert stats["admin_users"] >= 1
    assert stats["total_foods"] >= 3
    assert stats["total_daily_logs"] >= 1
    assert stats["total_food_entries"] >= 2


def test_get_stats_non_admin(authorized_client: TestClient):
    """Test getting system stats as non-admin user"""
    response = authorized_client.get("/api/v1/admin/stats")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_get_stats_unauthorized(client: TestClient):
    """Test getting system stats without authentication"""
    response = client.get("/api/v1/admin/stats")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_user_activity_admin(admin_client: TestClient):
    """Test getting user activity as admin"""
    response = admin_client.get("/api/v1/admin/users-activity")
    assert response.status_code == 200

    data = response.json()
    assert "time_period" in data
    assert "total_active_users" in data
    assert "users" in data


def test_get_user_activity_custom_days(admin_client: TestClient):
    """Test getting user activity with custom days parameter"""
    response = admin_client.get("/api/v1/admin/users-activity?days=7")
    assert response.status_code == 200

    data = response.json()
    assert "time_period" in data
    assert "total_active_users" in data
    assert "users" in data


def test_get_user_activity_non_admin(authorized_client: TestClient):
    """Test getting user activity as non-admin user"""
    response = authorized_client.get("/api/v1/admin/users-activity")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]
