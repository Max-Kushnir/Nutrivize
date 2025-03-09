import pytest
import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from jose import jwt, JWTError

from backend.models import User
from backend.database.db import Base
from backend.config import settings
from backend.auth.security import get_password_hash, verify_password, create_access_token
from backend.auth.auth import authenticate_user, get_current_user
from backend.crud.user import user_crud

# Database configuration
TEST_DB_URL = (
    f"postgresql://{settings.POSTGRES_USER}:"
    f"{settings.POSTGRES_PASSWORD}@"
    f"{settings.POSTGRES_HOST}:"
    f"{settings.POSTGRES_PORT}/"
    f"{settings.POSTGRES_TEST_DB}"
)

# Database fixtures
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

# Authentication integration tests
def test_authenticate_user_valid_credentials(db_session, test_user):
    """Test authentication with username"""
    user = authenticate_user(db_session, "testuser", "password123")
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"

def test_authenticate_user_with_email(db_session, test_user):
    """Test authentication with email"""
    user = authenticate_user(db_session, "testuser@example.com", "password123")
    assert user is not None
    assert user.username == "testuser" 
    assert user.email == "testuser@example.com"

def test_authenticate_user_wrong_password(db_session, test_user):
    """Test authentication with wrong password"""
    user = authenticate_user(db_session, "testuser", "wrongpassword")
    assert user is None

def test_authenticate_user_nonexistent(db_session):
    """Test authentication with non-existent user"""
    user = authenticate_user(db_session, "nonexistent", "password123")
    assert user is None

@pytest.mark.asyncio
async def test_get_current_user_valid_token(db_session, test_user, test_user_token):
    """Test getting current user with valid token"""
    user = await get_current_user(db=db_session, token=test_user_token)
    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"

@pytest.mark.asyncio
async def test_get_current_user_expired_token(db_session, test_user):
    """Test getting current user with expired token"""
    # Create an expired token
    expired_data = {"sub": test_user.username}
    expire = datetime.datetime.now(datetime.UTC) - datetime.timedelta(minutes=30)
    expired_data.update({"exp": expire})
    expired_token = jwt.encode(
        expired_data,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    
    with pytest.raises(Exception) as exc_info:
        await get_current_user(db=db_session, token=expired_token)
    
    assert "Could not validate credentials" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_current_user_tampered_token(db_session, test_user):
    """Test getting current user with tampered token"""
    # Create a tampered token (signed with different key)
    token = jwt.encode(
        {"sub": test_user.username},
        "wrong-secret-key",
        algorithm=settings.ALGORITHM
    )
    
    with pytest.raises(Exception) as exc_info:
        await get_current_user(db=db_session, token=token)
    
    assert "Could not validate credentials" in str(exc_info.value)

@pytest.mark.asyncio
async def test_get_current_user_nonexistent_user(db_session):
    """Test getting current user when username in token doesn't exist"""
    token = create_access_token({"sub": "nonexistent"})
    
    with pytest.raises(Exception) as exc_info:
        await get_current_user(db=db_session, token=token)
    
    assert "Could not validate credentials" in str(exc_info.value)

def test_password_hashing_and_verification(db_session):
    """Test that password hashing and verification work together"""
    original_password = "securepassword123"
    hashed = get_password_hash(original_password)
    
    assert verify_password(original_password, hashed) == True
    assert verify_password("wrongpassword", hashed) == False

def test_access_token_creation_and_verification(test_user):
    """Test creating and verifying access tokens"""
    token = create_access_token({"sub": test_user.username})
    
    # Verify token can be decoded
    payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    assert payload["sub"] == "testuser"
    assert "exp" in payload
    
    # Check token expiry is in the future
    now = datetime.datetime.now(datetime.UTC).timestamp()
    assert payload["exp"] > now

def test_inactive_user(db_session, test_user):
    """Test authentication with inactive user"""
    # Deactivate the user
    test_user.is_active = False
    db_session.commit()
    
    # Authentication should still work - is_active is checked separately
    user = authenticate_user(db_session, "testuser", "password123")
    assert user is not None
    assert user.is_active == False

def test_multiple_users(db_session, test_user):
    """Test authentication with multiple users in the database"""
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
    
    # Test first user authentication
    user1 = authenticate_user(db_session, "testuser", "password123")
    assert user1 is not None
    assert user1.username == "testuser"
    
    # Test second user authentication
    user2_auth = authenticate_user(db_session, "testuser2", "password456")
    assert user2_auth is not None
    assert user2_auth.username == "testuser2"

def test_wrong_algorithm_token(db_session, test_user):
    """Test token verification with wrong algorithm"""
    # Create token with different algorithm
    if settings.ALGORITHM == "HS256":
        different_alg = "HS512"
    else:
        different_alg = "HS256"
        
    token = jwt.encode(
        {"sub": test_user.username},
        settings.SECRET_KEY,
        algorithm=different_alg
    )
    
    # Trying to decode with expected algorithm should fail
    with pytest.raises(JWTError):
        jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])