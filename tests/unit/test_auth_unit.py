import pytest
from datetime import datetime, timedelta, UTC
from unittest.mock import MagicMock, patch
from jose import jwt
from fastapi import HTTPException

from backend.auth.security import verify_password, get_password_hash, create_access_token
from backend.auth.auth import authenticate_user, get_current_user
from backend.config import settings
from backend.models.user import User

# Test fixtures

@pytest.fixture
def mock_db():
    """Fixture for a mocked database session"""
    db = MagicMock()
    return db

@pytest.fixture
def test_user():
    """Fixture for a test user object"""
    user = MagicMock(spec=User)
    user.username = "testuser"
    user.email = "test@example.com"
    user.hashed_password = get_password_hash("password123")
    user.is_active = True
    return user

@pytest.fixture
def valid_token():
    """Fixture for a valid JWT token"""
    return create_access_token({"sub": "testuser"})

@pytest.fixture
def expired_token():
    """Fixture for an expired JWT token"""
    to_encode = {"sub": "testuser"}
    expire = datetime.now(UTC) - timedelta(minutes=1)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

# Unit tests for security.py functions

def test_password_hashing():
    """Test that password hashing works properly"""
    password = "securepassword123"
    hashed = get_password_hash(password)
    
    # Check that the hash is not the same as the original password
    assert hashed != password
    
    # Check that the same password produces different hashes (due to salt)
    hashed2 = get_password_hash(password)
    assert hashed != hashed2
    
    # Check that verification works
    assert verify_password(password, hashed)
    assert not verify_password("wrongpassword", hashed)

def test_create_access_token():
    """Test token creation with various parameters"""
    # Test with default expiration
    data = {"sub": "testuser"}
    token = create_access_token(data)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert payload["sub"] == "testuser"
    assert "exp" in payload
    
    # Verify that token expires in the future (roughly ACCESS_TOKEN_EXPIRE_MINUTES)
    now = datetime.now(UTC).timestamp()
    assert payload["exp"] > now
    assert payload["exp"] <= now + (settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60) + 10  # Adding buffer for test execution
    
    # Test with custom expiration
    custom_expire = timedelta(minutes=10)
    token = create_access_token(data, expires_delta=custom_expire)
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    
    assert payload["sub"] == "testuser"
    assert payload["exp"] <= now + 610  # 10 minutes + 10 seconds buffer

# Unit tests for auth.py functions

def test_authenticate_user_success_username(mock_db, test_user):
    """Test authentication with correct username and password"""
    with patch("backend.crud.user.user_crud.get_by_username", return_value=test_user):
        with patch("backend.crud.user.user_crud.get_by_email", return_value=None):
            user = authenticate_user(mock_db, "testuser", "password123")
            assert user is not None
            assert user.username == "testuser"

def test_authenticate_user_success_email(mock_db, test_user):
    """Test authentication with correct email and password"""
    with patch("backend.crud.user.user_crud.get_by_username", return_value=None):
        with patch("backend.crud.user.user_crud.get_by_email", return_value=test_user):
            user = authenticate_user(mock_db, "test@example.com", "password123")
            assert user is not None
            assert user.email == "test@example.com"

def test_authenticate_user_wrong_password(mock_db, test_user):
    """Test authentication with wrong password"""
    with patch("backend.crud.user.user_crud.get_by_username", return_value=test_user):
        user = authenticate_user(mock_db, "testuser", "wrongpassword")
        assert user is None

def test_authenticate_user_nonexistent(mock_db):
    """Test authentication with non-existent user"""
    with patch("backend.crud.user.user_crud.get_by_username", return_value=None):
        with patch("backend.crud.user.user_crud.get_by_email", return_value=None):
            user = authenticate_user(mock_db, "nonexistent", "password123")
            assert user is None

@pytest.mark.asyncio
async def test_get_current_user_success(mock_db, test_user, valid_token):
    """Test getting current user with valid token"""
    with patch("backend.crud.user.user_crud.get_by_username", return_value=test_user):
        user = await get_current_user(db=mock_db, token=valid_token)
        assert user is not None
        assert user.username == "testuser"

@pytest.mark.asyncio
async def test_get_current_user_invalid_token(mock_db):
    """Test getting current user with invalid token format"""
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=mock_db, token="invalid-token-format")
    
    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_current_user_expired_token(mock_db, expired_token):
    """Test getting current user with expired token"""
    with pytest.raises(HTTPException) as excinfo:
        await get_current_user(db=mock_db, token=expired_token)
    
    assert excinfo.value.status_code == 401
    assert "Could not validate credentials" in excinfo.value.detail

@pytest.mark.asyncio
async def test_get_current_user_user_not_found(mock_db, valid_token):
    """Test getting current user when user doesn't exist in DB"""
    with patch("backend.crud.user.user_crud.get_by_username", return_value=None):
        with pytest.raises(HTTPException) as excinfo:
            await get_current_user(db=mock_db, token=valid_token)
        
        assert excinfo.value.status_code == 401
        assert "Could not validate credentials" in excinfo.value.detail

# Security-focused tests

def test_token_tampering():
    """Test that tampered tokens are rejected"""
    # Generate valid token
    token = create_access_token({"sub": "testuser"})
    
    # Decode without verification
    payload = jwt.decode(token, settings.SECRET_KEY, options={"verify_signature": False}, algorithms=[settings.ALGORITHM])
    
    # Tamper with payload
    payload["sub"] = "admin"
    
    # Re-encode with different key
    tampered_token = jwt.encode(payload, "different-secret-key", algorithm=settings.ALGORITHM)
    
    # Verify it cannot be decoded with the real key
    with pytest.raises(jwt.JWTError):
        jwt.decode(tampered_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

def test_algorithm_change():
    """Test that tokens with wrong algorithm are rejected"""
    # Encode with different algorithm
    if settings.ALGORITHM == "HS256":
        different_alg = "HS512"
    else:
        different_alg = "HS256"
        
    token = jwt.encode({"sub": "testuser"}, settings.SECRET_KEY, algorithm=different_alg)
    
    # Attempt to decode with wrong algorithm should fail
    with pytest.raises(jwt.JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])

# Performance tests

def test_auth_performance():
    """Test authentication performance"""
    import time
    
    # Measure password hashing time
    start = time.time()
    hashed = get_password_hash("password123")
    hash_time = time.time() - start
    
    # Password hashing should take a reasonable amount of time for security
    # but not too long for usability
    assert 0.01 < hash_time < 1, f"Password hashing took {hash_time} seconds"
    
    # Measure token creation and verification time
    start = time.time()
    token = create_access_token({"sub": "testuser"})
    token_time = time.time() - start
    
    start = time.time()
    jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    verify_time = time.time() - start
    
    # Token operations should be relatively fast
    assert token_time < 0.01, f"Token creation took {token_time} seconds"
    assert verify_time < 0.01, f"Token verification took {verify_time} seconds"