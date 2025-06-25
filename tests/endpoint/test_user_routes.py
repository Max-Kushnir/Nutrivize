import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from backend.main import app
from backend.models import User
from backend.auth.security import get_password_hash


def test_get_all_users_admin(admin_client: TestClient, db_session: Session, test_user, test_admin):
    """Test getting all users as admin"""
    response = admin_client.get("/api/v1/users/")
    assert response.status_code == 200

    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 2

    usernames = [user["username"] for user in data]
    assert test_user.username in usernames
    assert test_admin.username in usernames


def test_get_all_users_non_admin(authorized_client: TestClient):
    """Test getting all users as non-admin user"""
    response = authorized_client.get("/api/v1/users/")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_get_all_users_unauthorized(client: TestClient):
    """Test getting all users without authentication"""
    response = client.get("/api/v1/users/")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_get_user_by_id_admin(admin_client: TestClient, test_user):
    """Test getting specific user by ID as admin"""
    response = admin_client.get(f"/api/v1/users/{test_user.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_user.id


def test_get_nonexistent_user_admin(admin_client: TestClient):
    """Test getting non-existent user as admin"""
    response = admin_client.get("/api/v1/users/9999")
    assert response.status_code == 404
    assert "User not found" in response.json()["detail"]


def test_get_user_by_id_non_admin(authorized_client: TestClient, test_admin):
    """Test getting user by ID as non-admin"""
    response = authorized_client.get(f"/api/v1/users/{test_admin.id}")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_update_user_admin(admin_client: TestClient, test_user, db_session: Session):
    """Test updating user as admin"""
    update_data = {
        "username": "updated_username",
        "email": "updated@example.com"
    }

    response = admin_client.put(f"/api/v1/users/{test_user.id}", json=update_data)
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == update_data["username"]
    assert data["email"] == update_data["email"]

    updated_user = db_session.query(User).filter(User.id == test_user.id).first()
    assert updated_user.username == update_data["username"]


def test_update_user_to_existing_username(admin_client: TestClient, test_user, test_admin):
    """Test updating user to an already existing username"""
    update_data = {
        "username": test_admin.username,
        "email": "new@example.com"
    }

    response = admin_client.put(f"/api/v1/users/{test_user.id}", json=update_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_update_user_to_existing_email(admin_client: TestClient, test_user, test_admin):
    """Test updating user to an already existing email"""
    update_data = {
        "username": "new_username",
        "email": test_admin.email
    }

    response = admin_client.put(f"/api/v1/users/{test_user.id}", json=update_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_update_user_non_admin(authorized_client: TestClient, test_admin):
    """Test updating user as non-admin"""
    update_data = {
        "username": "hacker_attempt",
        "email": "hacked@example.com"
    }

    response = authorized_client.put(f"/api/v1/users/{test_admin.id}", json=update_data)
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]


def test_delete_user_admin(admin_client: TestClient, db_session: Session):
    """Test deleting user as admin"""
    user_to_delete = User(
        username="delete_me",
        email="delete@example.com",
        hashed_password=get_password_hash("password123"),
        is_active=True,
        role="user"
    )
    db_session.add(user_to_delete)
    db_session.commit()
    db_session.refresh(user_to_delete)

    user_id = user_to_delete.id
    response = admin_client.delete(f"/api/v1/users/{user_id}")
    assert response.status_code == 204

    deleted_user = db_session.query(User).filter(User.id == user_id).first()
    assert deleted_user is None


def test_delete_self_admin(admin_client: TestClient, test_admin):
    """Test admin attempting to delete themselves"""
    response = admin_client.delete(f"/api/v1/users/{test_admin.id}")
    assert response.status_code == 400
    assert "Cannot delete your own account" in response.json()["detail"]


def test_delete_user_non_admin(authorized_client: TestClient, test_admin):
    """Test deleting user as non-admin"""
    response = authorized_client.delete(f"/api/v1/users/{test_admin.id}")
    assert response.status_code == 403
    assert "Insufficient permissions" in response.json()["detail"]
