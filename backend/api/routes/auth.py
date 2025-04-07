from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from backend.database.db import get_db
from backend.auth import authenticate_user, create_access_token, get_current_user
from backend.schemas.token import Token
from backend.schemas.user import UserCreate, UserResponse
from backend.crud.user import user_crud
from backend.auth.security import get_password_hash
from backend.config import settings
from backend.models.user import User
from backend.api.dependancies import get_current_active_user

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_create: UserCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new user
    """
    # Check if username already exists
    if user_crud.get_by_username(db, user_create.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    # Check if email already exists
    if user_crud.get_by_email(db, user_create.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Hash the password
    hashed_password = get_password_hash(user_create.password)
    
    # Create user object with hashed password
    user_data = user_create.model_dump(exclude={"password"})
    user_data["hashed_password"] = hashed_password
    user_data["is_active"] = True
    
    # Create the user in the database
    db_user = user_crud.create(db, user_data)
    
    return db_user

@router.post("/login", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Login a user using username/email and password
    """
    # This is just a wrapper around the token endpoint
    return await login_for_access_token(form_data, db)

@router.post("/logout")
async def logout(response: Response):
    """
    Logout the current user
    
    Note: Since JWT tokens are stateless, true logout on the server-side
    would require implementing a token blacklist or using short-lived tokens.
    This implementation simply instructs the client to remove the token.
    """
    # Clear the cookie if you're using cookies for tokens
    response.delete_cookie(key="access_token")
    return {"detail": "Successfully logged out"}

@router.post("/refresh", response_model=Token)
async def refresh_token(
    current_user: User = Depends(get_current_active_user)
):
    """
    Refresh the access token for the current user
    """
    # Create a new access token with potentially extended duration
    expires_delta = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": current_user.username},
        expires_delta=expires_delta
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=UserResponse)
async def get_current_user_details(
    current_user: User = Depends(get_current_active_user)
):
    """
    Get details of the currently authenticated user
    """
    return current_user

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    Get an access token using username/email and password.
    This endpoint can be used for the POST /auth/login route.
    """
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}