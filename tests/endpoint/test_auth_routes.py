import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from jose import jwt

from backend.main import app
from backend.config import settings
from backend.models import User
from backend.auth.security import get_password_hash


@pytest.fixture
def user_data():
    return {
        "username": "endpointuser",
        "email": "endpoint@example.com",
        "password": "password123"
    }


def test_register_user(client: TestClient, db_session: Session):
    """Test user registration endpoint"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "securepassword123"
    }

    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 201
    data = response.json()

    assert data["username"] == user_data["username"]
    assert data["email"] == user_data["email"]
    assert "id" in data
    assert "hashed_password" not in data

    created_user = db_session.query(User).filter(User.username == user_data["username"]).first()
    assert created_user is not None
    assert created_user.email == user_data["email"]


def test_register_user_duplicate_username(client: TestClient, db_session: Session, test_user):
    """Test registration with already existing username"""
    user_data = {
        "username": "testuser",  # Same as test_user fixture
        "email": "different@example.com",
        "password": "securepassword123"
    }

    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_register_user_duplicate_email(client: TestClient, db_session: Session, test_user):
    """Test registration with already existing email"""
    user_data = {
        "username": "differentuser",
        "email": "test@example.com",  # Same as test_user fixture
        "password": "securepassword123"
    }

    response = client.post("/api/v1/auth/register", json=user_data)
    assert response.status_code == 400
    assert "already registered" in response.json()["detail"]


def test_login_valid_credentials(client: TestClient, user_data, db_session: Session):
    """Test login with valid credentials"""
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()

    login_data = {
        "username": user_data["username"],
        "password": user_data["password"]
    }

    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

    token = data["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == user_data["username"]


def test_login_with_email(client: TestClient, user_data, db_session: Session):
    """Test login using email instead of username"""
    user = User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=get_password_hash(user_data["password"]),
        is_active=True,
        role="user"
    )
    db_session.add(user)
    db_session.commit()

    login_data = {
        "username": user_data["email"],  # Using email in username field
        "password": user_data["password"]
    }

    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 200
    assert "access_token" in response.json()


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials"""
    login_data = {
        "username": "nonexistentuser",
        "password": "wrongpassword"
    }

    response = client.post("/api/v1/auth/login", data=login_data)
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]


def test_get_current_user(client: TestClient, test_user, user_token):
    """Test getting current user details"""
    client.headers = {"Authorization": f"Bearer {user_token}"}

    response = client.get("/api/v1/auth/me")
    assert response.status_code == 200

    data = response.json()
    assert data["username"] == test_user.username
    assert data["email"] == test_user.email
    assert "hashed_password" not in data


def test_get_current_user_unauthorized(client: TestClient):
    """Test getting current user with no token"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]


def test_refresh_token(client: TestClient, test_user, user_token):
    """Test refreshing access token"""
    client.headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post("/api/v1/auth/refresh")
    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"
    assert data["access_token"] != user_token


def test_logout(client: TestClient, user_token):
    """Test logout endpoint"""
    client.headers = {"Authorization": f"Bearer {user_token}"}

    response = client.post("/api/v1/auth/logout")
    assert response.status_code == 200
    assert "Successfully logged out" in response.json()["detail"]
