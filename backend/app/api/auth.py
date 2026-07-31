from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.core.database import get_db
from app.core.security import hash_password, verify_password, create_access_token, get_current_user
from app.core.config import settings
from app.models.models import User
from app.schemas.schemas import UserRegister, UserLogin, SuccessResponse, TokenOut, UserOut

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=SuccessResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """POST /api/v1/auth/register - Register a new recruiter account."""
    existing = db.query(User).filter(User.email == user_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error_code": "EMAIL_ALREADY_EXISTS", "error_detail": "Email is already registered"}
        )
    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        hashed_password=hash_password(user_data.password),
        role=user_data.role
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return SuccessResponse(
        status_message="User registered successfully",
        payload=UserOut.model_validate(new_user)
    )


@router.post("/login", response_model=SuccessResponse)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """POST /api/v1/auth/login - Login and get JWT token."""
    user = db.query(User).filter(User.email == credentials.email).first()
    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "INVALID_CREDENTIALS", "error_detail": "Invalid email or password"}
        )
    token = create_access_token(
        data={"sub": str(user.id)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return SuccessResponse(
        status_message="Login successful",
        payload=TokenOut(
            access_token=token,
            token_type="bearer",
            user=UserOut.model_validate(user)
        )
    )


@router.post("/logout", response_model=SuccessResponse)
def logout(current_user: User = Depends(get_current_user)):
    """POST /api/v1/auth/logout - Logout (client-side token invalidation)."""
    return SuccessResponse(status_message="Logged out successfully", payload=None)


@router.get("/profile", response_model=SuccessResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    """GET /api/v1/auth/profile - Get current user profile."""
    return SuccessResponse(
        status_message="Profile retrieved",
        payload=UserOut.model_validate(current_user)
    )
