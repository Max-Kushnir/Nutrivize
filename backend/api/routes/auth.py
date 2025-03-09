from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from backend.database.db import get_db
from backend.auth import authenticate_user, create_access_token
from backend.schema.token import Token
from backend.schema.user import UserCreate, UserResponse
from backend.crud.user import user_crud

router = APIRouter(
    prefix="/auth",
    tags=["authentication"]
)

# POST /auth/register - Register a new user


# POST /auth/login - User login (returns JWT)


# POST /auth/logout - Logout


# POST /auth/refresh - Refresh token


# GET /auth/me - Get current user details

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
