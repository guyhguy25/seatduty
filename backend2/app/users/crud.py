from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.users.models import User
from app.users.schemas import UserCreate, UserUpdate, UserSearch
from app.core.security import get_password_hash


class UserCRUD:
    def create(self, db: Session, user: UserCreate) -> User:
        """Create a new user."""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            hashed_password=hashed_password,
            name=user.name,
            phone=user.phone,
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_by_id(self, db: Session, user_id: int) -> Optional[User]:
        """Get user by ID."""
        return db.query(User).filter(User.id == user_id).first()

    def get_by_email(self, db: Session, email: str) -> Optional[User]:
        """Get user by email."""
        return db.query(User).filter(User.email == email).first()

    def get_multi(self, db: Session, skip: int = 0, limit: int = 100) -> List[User]:
        """Get multiple users with pagination."""
        return db.query(User).offset(skip).limit(limit).all()

    def search(self, db: Session, search: UserSearch) -> tuple[List[User], int]:
        """Search users with filters and pagination."""
        query = db.query(User)
        
        # Apply filters
        if search.email:
            query = query.filter(User.email.ilike(f"%{search.email}%"))
        if search.name:
            query = query.filter(User.name.ilike(f"%{search.name}%"))
        if search.is_active is not None:
            query = query.filter(User.is_active == search.is_active)
        
        # Get total count
        total = query.count()
        
        # Apply pagination
        offset = (search.page - 1) * search.limit
        users = query.offset(offset).limit(search.limit).all()
        
        return users, total

    def update(self, db: Session, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user."""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        if "password" in update_data:
            update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
        
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete(self, db: Session, user_id: int) -> bool:
        """Delete user."""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return False
        
        db.delete(db_user)
        db.commit()
        return True

    def bulk_delete(self, db: Session, user_ids: List[int]) -> int:
        """Delete multiple users."""
        deleted_count = db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
        db.commit()
        return deleted_count

    def bulk_update(self, db: Session, user_ids: List[int], update_data: dict) -> int:
        """Update multiple users."""
        updated_count = db.query(User).filter(User.id.in_(user_ids)).update(
            update_data, synchronize_session=False
        )
        db.commit()
        return updated_count

    def toggle_active(self, db: Session, user_id: int) -> Optional[User]:
        """Toggle user active status."""
        db_user = self.get_by_id(db, user_id)
        if not db_user:
            return None
        
        db_user.is_active = not db_user.is_active
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user

    def get_active_users(self, db: Session) -> List[User]:
        """Get all active users."""
        return db.query(User).filter(User.is_active == True).all()

    def get_superusers(self, db: Session) -> List[User]:
        """Get all superusers."""
        return db.query(User).filter(User.is_superuser == True).all()


# Create instance
user_crud = UserCRUD()
