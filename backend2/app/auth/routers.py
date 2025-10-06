from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.core.database import get_db
from app.users.models import User
from app.users.schemas import UserCreate, UserOut
from app.auth.schemas import (
    LoginRequest, Token, RefreshTokenRequest, ForgotPasswordRequest,
    ResetPasswordRequest, LogoutRequest
)
from app.core.security import (
    get_password_hash, verify_password, create_access_token, 
    create_refresh_token, create_password_reset_token,
    decode_token, is_token_expired
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)):
    """Register a new user."""
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=get_password_hash(payload.password),
        name=payload.name,
        phone=payload.phone,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    """Login user and return tokens."""
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
    
    access_token = create_access_token(subject=str(user.id))
    refresh_token = create_refresh_token(subject=str(user.id))
    
    # Store refresh token in database
    user.refresh_token = refresh_token
    db.add(user)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": refresh_token}


@router.post("/refresh", response_model=Token)
def refresh_token(payload: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token."""
    # Verify refresh token
    token_data = decode_token(payload.refresh_token)
    if not token_data or token_data.get("type") != "refresh" or is_token_expired(token_data):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    user = db.query(User).filter(User.id == int(token_data["sub"])).first()
    if not user or user.refresh_token != payload.refresh_token:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    
    # Generate new tokens
    access_token = create_access_token(subject=str(user.id))
    new_refresh_token = create_refresh_token(subject=str(user.id))
    
    # Update refresh token in database
    user.refresh_token = new_refresh_token
    db.add(user)
    db.commit()
    
    return {"access_token": access_token, "token_type": "bearer", "refresh_token": new_refresh_token}


@router.post("/logout")
def logout(payload: LogoutRequest, db: Session = Depends(get_db)):
    """Logout user by invalidating refresh token."""
    user = db.query(User).filter(User.refresh_token == payload.refresh_token).first()
    if user:
        user.refresh_token = None
        db.add(user)
        db.commit()
    return {"message": "Logged out successfully"}


@router.post("/forgot-password")
def forgot_password(payload: ForgotPasswordRequest, db: Session = Depends(get_db)):
    """Send password reset token."""
    user = db.query(User).filter(User.email == payload.email).first()
    if not user:
        # Don't reveal if email exists
        return {"message": "If the email exists, a password reset link has been sent"}
    
    # Generate reset token
    reset_token = create_password_reset_token()
    reset_expires = datetime.now(timezone.utc).replace(tzinfo=None) + timedelta(hours=1)
    
    user.reset_token = reset_token
    user.reset_token_expires = reset_expires
    db.add(user)
    db.commit()
    
    # In production, send email here
    # For now, we'll return the token for testing
    return {
        "message": "Password reset token generated",
        "reset_token": reset_token,  # Remove in production
        "expires_in": "1 hour"
    }


@router.post("/reset-password")
def reset_password(payload: ResetPasswordRequest, db: Session = Depends(get_db)):
    """Reset password using reset token."""
    try:
        user = db.query(User).filter(User.reset_token == payload.token).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid reset token")
        
        if not user.reset_token_expires:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired")
        
        if user.reset_token_expires < datetime.now(timezone.utc).replace(tzinfo=None):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Reset token has expired")
        
        # Update password and clear reset token
        user.hashed_password = get_password_hash(payload.new_password)
        user.reset_token = None
        user.reset_token_expires = None
        user.refresh_token = None  # Invalidate all sessions
        db.add(user)
        db.commit()
        
        return {"message": "Password reset successfully"}
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Internal server error: {str(e)}")
