from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.deps import get_current_user
from app.users.models import User
from app.users.schemas import (
    UserCreate, UserOut, UserList, UserSearch,
    UserBulkDelete, UserBulkUpdate, AdminUserUpdate,
)
from app.users.crud import user_crud
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


# User Management (Admin Only)

@router.post("/users", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Create a new user (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # Check if email already exists
    existing_user = user_crud.get_by_email(db, user_data.email)
    if existing_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    
    return user_crud.create(db, user_data)


@router.get("/users", response_model=UserList)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    email: str = Query(None, description="Filter by email"),
    name: str = Query(None, description="Filter by name"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get users list with pagination and filtering (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    search = UserSearch(
        email=email,
        name=name,
        is_active=is_active,
        page=page,
        limit=limit
    )
    
    users, total = user_crud.search(db, search)
    
    return UserList(
        users=users,
        total=total,
        page=page,
        limit=limit
    )


@router.get("/users/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user by ID (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.put("/users/{user_id}", response_model=UserOut)
def update_user(
    user_id: int,
    user_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user by ID (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    updated_user = user_crud.update(db, user_id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user


@router.delete("/users/{user_id}")
def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete user by ID (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # Prevent self-deletion
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    
    success = user_crud.delete(db, user_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return {"message": "User deleted successfully"}


@router.post("/users/bulk-delete")
def bulk_delete_users(
    bulk_data: UserBulkDelete,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete multiple users (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # Prevent self-deletion
    if current_user.id in bulk_data.user_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own account")
    
    deleted_count = user_crud.bulk_delete(db, bulk_data.user_ids)
    return {"message": f"Successfully deleted {deleted_count} users"}


@router.put("/users/bulk-update")
def bulk_update_users(
    bulk_data: UserBulkUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update multiple users (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    update_data = bulk_data.dict(exclude={"user_ids"}, exclude_unset=True)
    if not update_data:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No update data provided")
    
    updated_count = user_crud.bulk_update(db, bulk_data.user_ids, update_data)
    return {"message": f"Successfully updated {updated_count} users"}


@router.patch("/users/{user_id}/toggle-active")
def toggle_user_active(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Toggle user active status (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    # Prevent self-deactivation
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot deactivate your own account")
    
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    user.is_active = not user.is_active
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return {"message": f"User {'activated' if user.is_active else 'deactivated'} successfully"}


@router.get("/users/stats/active")
def get_active_users_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get active users statistics (admin only)."""
    if not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    
    active_users = user_crud.get_active_users(db)
    return {"active_users": active_users}
