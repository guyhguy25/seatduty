import os
import logging
from sqlalchemy.orm import Session
from app.core.database import SessionLocal, engine, Base
from app.users.models import User
from app.core.security import get_password_hash

logger = logging.getLogger(__name__)


def init_db() -> None:
    """Initialize database with default admin user."""
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        logger.info("✅ Database tables created successfully")
        
        # Create database session
        db = SessionLocal()
        
        try:
            # Check if admin user already exists
            admin_email = os.getenv("ADMIN_EMAIL", "admin@seatduty.com")
            existing_admin = db.query(User).filter(User.email == admin_email).first()
            
            if existing_admin:
                logger.info(f"✅ Admin user already exists: {admin_email}")
                return
            
            # Create default admin user
            admin_password = os.getenv("ADMIN_PASSWORD", "admin123")
            admin_name = os.getenv("ADMIN_NAME", "System Administrator")
            
            admin_user = User(
                email=admin_email,
                hashed_password=get_password_hash(admin_password),
                name=admin_name,
                phone=os.getenv("ADMIN_PHONE", "+1234567890"),
                is_active=True,
                is_superuser=True
            )
            
            db.add(admin_user)
            db.commit()
            db.refresh(admin_user)
            
            logger.info(f"✅ Default admin user created successfully!")
            logger.info(f"📧 Email: {admin_email}")
            logger.info(f"🔑 Password: {admin_password}")
            logger.info(f"👤 Name: {admin_name}")
            logger.info("⚠️  Please change the default password after first login!")
            
        except Exception as e:
            logger.error(f"❌ Error creating admin user: {e}")
            db.rollback()
            raise
        finally:
            db.close()
            
    except Exception as e:
        logger.error(f"❌ Database initialization failed: {e}")
        raise


def create_superuser(email: str, password: str, name: str = "Superuser") -> User:
    """Create a superuser programmatically."""
    db = SessionLocal()
    try:
        # Check if user already exists
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
            raise ValueError(f"User with email {email} already exists")
        
        # Create superuser
        superuser = User(
            email=email,
            hashed_password=get_password_hash(password),
            name=name,
            is_active=True,
            is_superuser=True
        )
        
        db.add(superuser)
        db.commit()
        db.refresh(superuser)
        
        logger.info(f"✅ Superuser created: {email}")
        return superuser
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error creating superuser: {e}")
        raise
    finally:
        db.close()


def reset_admin_password(email: str, new_password: str) -> bool:
    """Reset admin user password."""
    db = SessionLocal()
    try:
        admin_user = db.query(User).filter(
            User.email == email,
            User.is_superuser == True
        ).first()
        
        if not admin_user:
            logger.error(f"❌ Admin user not found: {email}")
            return False
        
        admin_user.hashed_password = get_password_hash(new_password)
        admin_user.refresh_token = None  # Invalidate all sessions
        db.add(admin_user)
        db.commit()
        
        logger.info(f"✅ Admin password reset successfully: {email}")
        return True
        
    except Exception as e:
        db.rollback()
        logger.error(f"❌ Error resetting admin password: {e}")
        return False
    finally:
        db.close()
