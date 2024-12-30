from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from api.database.db import get_db
from api.crud.user import user_crud
from api.models.user import User
from api.config import settings
from .security import verify_password

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")

def authenticate_user(db: Session, username: str, password: str):
    """
    Verify a user's credentials using username instead of email
    """
    user = user_crud.get_by_username(db, username)  
    if not user:
        return False
    if not verify_password(password, user.hashed_password):
        return False
    return user

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
):
    """
    Get the current user from their JWT token
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        username: str = payload.get("sub")  
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    
    user = user_crud.get_by_username(db, username) 
    if user is None:
        raise credentials_exception
    return user