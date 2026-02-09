"""Authentication endpoints."""
import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserLogin, UserResponse
from app.schemas.token import Token
from app.core.security import get_password_hash, verify_password, create_access_token
from app.api.deps import get_current_user

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_in: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    try:
        if db.query(User).filter(User.username == user_in.username).first():
            raise HTTPException(
                status_code=400,
                detail="Username already registered",
            )
        if db.query(User).filter(User.email == user_in.email).first():
            raise HTTPException(
                status_code=400,
                detail="Email already registered",
            )
        user = User(
            username=user_in.username,
            email=user_in.email,
            password_hash=get_password_hash(user_in.password),
        )
        db.add(user)
        db.commit()
        db.refresh(user)
        return user
    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Registration failed")
        raise HTTPException(status_code=500, detail=f"Registration error: {str(e)}")


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """Login and return JWT access token."""
    user = db.query(User).filter(User.username == credentials.username).first()
    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    access_token = create_access_token(subject=user.username)
    return Token(access_token=access_token, token_type="bearer")


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    """Get current authenticated user."""
    return current_user
