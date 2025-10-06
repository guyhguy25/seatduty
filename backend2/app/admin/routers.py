from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.users.models import User
from app.core.init_db import create_superuser, reset_admin_password
from pydantic import BaseModel, EmailStr
from typing import List

router = APIRouter(prefix="/admin", tags=["admin"])


class CreateAdminRequest(BaseModel):
    email: EmailStr
    password: str
    name: str = "Administrator"


class ResetPasswordRequest(BaseModel):
    email: EmailStr
    new_password: str


@router.post("/create-admin")
def create_admin_user(
    request: CreateAdminRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new admin user (superuser only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser access required")
    
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == request.email).first()
        if existing_user:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="User already exists")
        
        # Create superuser
        admin_user = create_superuser(request.email, request.password, request.name)
        
        return {
            "message": "Admin user created successfully",
            "user": {
                "id": admin_user.id,
                "email": admin_user.email,
                "name": admin_user.name,
                "is_superuser": admin_user.is_superuser
            }
        }
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error creating admin: {str(e)}")


@router.post("/reset-admin-password")
def reset_admin_password_endpoint(
    request: ResetPasswordRequest,
    current_user: User = Depends(get_current_user)
):
    """Reset admin user password (superuser only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser access required")
    
    try:
        success = reset_admin_password(request.email, request.new_password)
        if success:
            return {"message": f"Password reset successfully for {request.email}"}
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Admin user not found")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error resetting password: {str(e)}")


@router.get("/list-admins")
def list_admin_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """List all admin users (superuser only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser access required")
    
    try:
        admins = db.query(User).filter(User.is_superuser == True).all()
        
        admin_list = []
        for admin in admins:
            admin_list.append({
                "id": admin.id,
                "email": admin.email,
                "name": admin.name,
                "phone": admin.phone,
                "is_active": admin.is_active,
                "created_at": admin.created_at,
                "updated_at": admin.updated_at
            })
        
        return {
            "admins": admin_list,
            "total": len(admin_list)
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error listing admins: {str(e)}")


@router.get("/system-info")
def get_system_info(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get system information (superuser only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser access required")
    
    try:
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        superusers = db.query(User).filter(User.is_superuser == True).count()
        
        return {
            "total_users": total_users,
            "active_users": active_users,
            "inactive_users": total_users - active_users,
            "superusers": superusers,
            "regular_users": total_users - superusers
        }
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Error getting system info: {str(e)}")
