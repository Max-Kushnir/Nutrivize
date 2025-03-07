import pytest
import os
import datetime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, Session
from jose import jwt
from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.testclient import TestClient

from backend.models import User
from backend.database.db import Base, get_db
from backend.config import settings
from backend.auth.security import get_password_hash, create_access_token
from backend.auth.auth import authenticate_user, get_current_user
from backend.crud.user import user_crud

# Database configuration (using your existing setup)
TEST_DB_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_TEST_DB}"
)

# Database fixtures (using your existing setup)
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
    yield session
    session.close()
    transaction.rollback()
    connection.close()

# Create a minimal test app fixture since main.py isn't available yet
@pytest.fixture(scope="function")
def test_app(db_session):
    """Create a minimal FastAPI app with auth endpoints for testing"""
    app = FastAPI()
    
    # Override the get_db dependency to use our test db_session
    def override_get_db():
        yield db_session
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Add token endpoint
    @app.post("/auth/token")
    async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
        user = authenticate_user(db_session, form_data.username, form_data.password)
        if not user:
            raise HTTPException(
                status_code=401,
                detail="Invalid authentication credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
        access_token = create_access_token(data={"sub": user.username})
        return {"access_token": access_token, "token_type": "bearer"}
    
    # Add a protected endpoint for testing
    @app.get("/users/me")
    async def read_users_me(current_user: User = Depends(get_current_user)):
        return {
            "id": current_user.id,
            "username": current_user.username,
            "email": current_user.email,
            "is_active": current_user.is_active
        }
    
    return app

@pytest.fixture(scope="function")
def client(test_app):
    with TestClient(test_app) as client:
        yield client

# Test user fixtures
@pytest.fixture(scope="function")
def test_user(db_session):
    """Create a test user in the database"""
    user_data = {
        "username": "testuser",
        "email": "testuser@example.com",
        "hashed_password": get_password_hash("password123"),
        "is_active": True
    }
    
    user = User(**user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture(scope="function")
def test_user_token(test_user):
    """Create a valid token for the test user"""
    return create_access_token({"sub": test_user.username})

# Authentication endpoint tests
def test_login_endpoint_success(client, test_user):
    """Test login with valid credentials"""
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "password123"}
    )
    
    assert response.status_code == 200
    json_response = response.json()
    assert "access_token" in json_response
    assert json_response["token_type"] == "bearer"
    
    # Verify token can be decoded
    token = json_response["access_token"]
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "testuser"

def test_login_with_email(client, test_user):
    """Test login with email instead of username"""
    response = client.post(
        "/auth/token",
        data={"username": "testuser@example.com", "password": "password123"}
    )
    
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_wrong_password(client, test_user):
    """Test login with wrong password"""
    response = client.post(
        "/auth/token",
        data={"username": "testuser", "password": "wrongpassword"}
    )
    
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]

def test_login_nonexistent_user(client):
    """Test login with non-existent user"""
    response = client.post(
        "/auth/token",
        data={"username": "nonexistent", "password": "password123"}
    )
    
    assert response.status_code == 401
    assert "Invalid authentication credentials" in response.json()["detail"]

# Protected endpoint tests
def test_access_protected_endpoint(client, test_user, test_user_token):
    """Test accessing a protected endpoint with valid token"""
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    assert response.status_code == 200
    user_data = response.json()
    assert user_data["username"] == "testuser"

def test_access_protected_endpoint_no_token(client):
    """Test accessing a protected endpoint without a token"""
    response = client.get("/users/me")
    assert response.status_code == 401
    assert "Not authenticated" in response.json()["detail"]

def test_access_protected_endpoint_invalid_token(client):
    """Test accessing a protected endpoint with invalid token"""
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer invalidtoken"}
    )
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

def test_access_protected_endpoint_expired_token(client, test_user):
    """Test accessing a protected endpoint with expired token"""
    # Create an expired token
    expired_data = {"sub": test_user.username}
    expire = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=30)
    expired_data.update({"exp": expire})
    expired_token = jwt.encode(
        expired_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {expired_token}"}
    )
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]

# Test token reuse
def test_token_reuse(client, test_user, test_user_token):
    """Test that the same token can be reused multiple times (unless you implement token blacklisting)"""
    # First request
    response1 = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response1.status_code == 200
    
    # Second request with the same token
    response2 = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    assert response2.status_code == 200

# Test inactive user
def test_inactive_user(client, db_session, test_user, test_user_token):
    """Test authentication with an inactive user account"""
    # Deactivate the user
    test_user.is_active = False
    db_session.commit()
    
    # Try to use the token that was created when the user was active
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {test_user_token}"}
    )
    
    # User should still be authenticated (unless you check for is_active in your get_current_user)
    # If you implement active user checking, update this assertion accordingly
    assert response.status_code == 200
    
    # If you have an active user check, use this instead:
    # assert response.status_code == 400
    # assert "Inactive user" in response.json()["detail"]

# Test concurrent access from different users
def test_multiple_users(client, db_session, test_user):
    """Test multiple users accessing protected endpoints simultaneously"""
    # Create a second user
    user2_data = {
        "username": "testuser2",
        "email": "testuser2@example.com",
        "hashed_password": get_password_hash("password456"),
        "is_active": True
    }
    
    user2 = User(**user2_data)
    db_session.add(user2)
    db_session.commit()
    db_session.refresh(user2)
    
    # Create tokens for both users
    token1 = create_access_token({"sub": test_user.username})
    token2 = create_access_token({"sub": user2.username})
    
    # Test first user
    response1 = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token1}"}
    )
    assert response1.status_code == 200
    assert response1.json()["username"] == "testuser"
    
    # Test second user
    response2 = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token2}"}
    )
    assert response2.status_code == 200
    assert response2.json()["username"] == "testuser2"

# Test malformed authorization header
def test_malformed_auth_header(client):
    """Test various malformed authorization headers"""
    # Missing 'Bearer' prefix
    response = client.get(
        "/users/me",
        headers={"Authorization": "validtoken12345"}
    )
    assert response.status_code == 401
    
    # Empty token
    response = client.get(
        "/users/me",
        headers={"Authorization": "Bearer "}
    )
    assert response.status_code == 401
    
    # Malformed header
    response = client.get(
        "/users/me",
        headers={"Authorization": "Something else"}
    )
    assert response.status_code == 401

# Test token with wrong signature algorithm
def test_wrong_algorithm_token(client, test_user):
    """Test token created with wrong algorithm"""
    if settings.ALGORITHM == "HS256":
        different_alg = "HS512"
    else:
        different_alg = "HS256"
        
    token = jwt.encode(
        {"sub": test_user.username},
        settings.SECRET_KEY,
        algorithm=different_alg
    )
    
    response = client.get(
        "/users/me",
        headers={"Authorization": f"Bearer {token}"}
    )
    
    assert response.status_code == 401
    assert "Could not validate credentials" in response.json()["detail"]