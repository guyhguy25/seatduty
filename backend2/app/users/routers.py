from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.core.deps import get_current_user
from app.users.models import User
from app.users.schemas import (
    UserList, UserSearch, UserUpdate, UserOut,
)
from app.users.crud import user_crud

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", response_model=UserList)
def get_users(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    email: str = Query(None, description="Filter by email"),
    name: str = Query(None, description="Filter by name"),
    is_active: bool = Query(None, description="Filter by active status"),
    db: Session = Depends(get_db)
):
    """Get users list with pagination and filtering."""
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

@router.get("/find/{user_id}", response_model=UserOut)
def get_user(
    user_id: int,
    db: Session = Depends(get_db)
):
    """Get user by ID."""
    user = user_crud.get_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user
@router.get("/profile", response_model=UserOut)
def get_profile(current_user: User = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user

@router.put("/profile", response_model=UserOut)
def update_profile(
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update current user's profile."""
    updated_user = user_crud.update(db, current_user.id, user_data)
    if not updated_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return updated_user

@router.delete("/account", status_code=status.HTTP_204_NO_CONTENT)
def delete_account(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete current user's account."""
    success = user_crud.delete(db, current_user.id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return None