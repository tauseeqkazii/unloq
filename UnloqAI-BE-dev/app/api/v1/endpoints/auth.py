from datetime import timedelta
from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.api import deps
from app.core import security
from app.core.config import settings
from app.models.shared import User
from pydantic import BaseModel, EmailStr

router = APIRouter()

@router.options("/signup")
def test_signup_options():
    from fastapi.responses import JSONResponse
    return JSONResponse(
        status_code=200,
        content={"message": "OPTIONS preflight success"},
        headers={
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "POST, GET, OPTIONS",
            "Access-Control-Allow-Headers": "*"
        }
    )

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    full_name: str = None

class UserResponse(BaseModel):
    id: Any
    email: str
    full_name: str = None
    is_active: bool

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str

@router.post("/signup", response_model=UserResponse)
def create_user(
    user_in: UserCreate,
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Create new user.
    """
    user = db.query(User).filter(User.email == user_in.email).first()
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this username already exists in the system.",
        )
    user = User(
        email=user_in.email,
        hashed_password=security.get_password_hash(user_in.password),
        full_name=user_in.full_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

@router.post("/login", response_model=Token)
def login_access_token(
    db: Session = Depends(deps.get_db),
    form_data: OAuth2PasswordRequestForm = Depends(),
) -> Any:
    """
    OAuth2 compatible token login, get an access token for future requests
    """
    user = db.query(User).filter(User.email == form_data.username).first()
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return {
        "access_token": security.create_access_token(
            user.id, expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }

@router.post("/logout")
def logout(
    token: str = Depends(deps.reusable_oauth2),
    db: Session = Depends(deps.get_db),
) -> Any:
    """
    Logout current user and blacklist token.
    """
    # Check if already blacklisted to avoid unique constraint error
    from app.models.shared import TokenBlacklist
    if db.query(TokenBlacklist).filter(TokenBlacklist.token == token).first():
        return {"msg": "Successfully logged out"}
        
    db_token = TokenBlacklist(token=token)
    db.add(db_token)
    db.commit()
    return {"msg": "Successfully logged out"}

