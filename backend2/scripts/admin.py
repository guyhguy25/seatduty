#!/usr/bin/env python3
"""
Admin management script for SeatDuty Backend.
"""
import os
import sys
import argparse
from pathlib import Path

# Add the app directory to Python path
sys.path.append(str(Path(__file__).parent.parent))

from app.core.init_db import create_superuser, reset_admin_password
from app.core.database import SessionLocal
from app.users.models import User
from app.core.security import get_password_hash


def create_admin(email: str, password: str, name: str = "Administrator"):
    """Create a new admin user."""
    try:
        user = create_superuser(email, password, name)
        print(f"✅ Admin user created successfully!")
        print(f"📧 Email: {email}")
        print(f"👤 Name: {name}")
        print(f"🔑 Password: {password}")
        return True
    except Exception as e:
        print(f"❌ Error creating admin: {e}")
        return False


def reset_password(email: str, new_password: str):
    """Reset admin password."""
    try:
        success = reset_admin_password(email, new_password)
        if success:
            print(f"✅ Password reset successfully for {email}")
        else:
            print(f"❌ Failed to reset password for {email}")
        return success
    except Exception as e:
        print(f"❌ Error resetting password: {e}")
        return False


def list_admins():
    """List all admin users."""
    db = SessionLocal()
    try:
        admins = db.query(User).filter(User.is_superuser == True).all()
        if not admins:
            print("No admin users found.")
            return
        
        print("👑 Admin Users:")
        print("-" * 50)
        for admin in admins:
            status = "🟢 Active" if admin.is_active else "🔴 Inactive"
            print(f"📧 {admin.email}")
            print(f"👤 {admin.name}")
            print(f"📱 {admin.phone}")
            print(f"📅 Created: {admin.created_at}")
            print(f"🔧 Status: {status}")
            print("-" * 50)
            
    except Exception as e:
        print(f"❌ Error listing admins: {e}")
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="SeatDuty Admin Management")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create admin command
    create_parser = subparsers.add_parser("create", help="Create a new admin user")
    create_parser.add_argument("email", help="Admin email")
    create_parser.add_argument("password", help="Admin password")
    create_parser.add_argument("--name", default="Administrator", help="Admin name")
    
    # Reset password command
    reset_parser = subparsers.add_parser("reset-password", help="Reset admin password")
    reset_parser.add_argument("email", help="Admin email")
    reset_parser.add_argument("password", help="New password")
    
    # List admins command
    subparsers.add_parser("list", help="List all admin users")
    
    args = parser.parse_args()
    
    if args.command == "create":
        create_admin(args.email, args.password, args.name)
    elif args.command == "reset-password":
        reset_password(args.email, args.password)
    elif args.command == "list":
        list_admins()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
