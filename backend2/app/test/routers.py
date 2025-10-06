from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.users.models import User
from fastapi.testclient import TestClient
import json

router = APIRouter(prefix="/test", tags=["testing"])


@router.post("/run-all")
def run_all_tests():
    """Run all tests and return results."""
    try:
        # Import app here to avoid circular import
        from server import app
        # Create test client
        client = TestClient(app)
        
        # Test results
        results = {
            "auth_tests": {},
            "user_tests": {},
            "summary": {
                "total": 0,
                "passed": 0,
                "failed": 0
            }
        }
        
        # Test 1: Register new user
        try:
            register_data = {
                "email": "testuser@example.com",
                "password": "testpassword123",
                "name": "Test User",
                "phone": "1234567890"
            }
            response = client.post("/auth/register", json=register_data)
            results["auth_tests"]["register"] = {
                "status": "PASS" if response.status_code == 201 else "FAIL",
                "status_code": response.status_code,
                "response": response.json()
            }
            if response.status_code == 201:
                results["summary"]["passed"] += 1
            else:
                results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        except Exception as e:
            results["auth_tests"]["register"] = {"status": "ERROR", "error": str(e)}
            results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        
        # Test 2: Login
        try:
            login_data = {
                "email": "testuser@example.com",
                "password": "testpassword123"
            }
            response = client.post("/auth/login", json=login_data)
            results["auth_tests"]["login"] = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "response": response.json()
            }
            if response.status_code == 200:
                results["summary"]["passed"] += 1
                access_token = response.json()["access_token"]
                headers = {"Authorization": f"Bearer {access_token}"}
            else:
                headers = None
            results["summary"]["total"] += 1
        except Exception as e:
            results["auth_tests"]["login"] = {"status": "ERROR", "error": str(e)}
            results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        
        # Test 3: Get profile (if login succeeded)
        if headers:
            try:
                response = client.get("/users/profile", headers=headers)
                results["user_tests"]["get_profile"] = {
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "status_code": response.status_code,
                    "response": response.json()
                }
                if response.status_code == 200:
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
            except Exception as e:
                results["user_tests"]["get_profile"] = {"status": "ERROR", "error": str(e)}
                results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
        
        # Test 4: Update profile
        if headers:
            try:
                update_data = {"name": "Updated Test User"}
                response = client.put("/users/profile", json=update_data, headers=headers)
                results["user_tests"]["update_profile"] = {
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "status_code": response.status_code,
                    "response": response.json()
                }
                if response.status_code == 200:
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
            except Exception as e:
                results["user_tests"]["update_profile"] = {"status": "ERROR", "error": str(e)}
                results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
        
        # Test 5: Forgot password
        try:
            forgot_data = {"email": "testuser@example.com"}
            response = client.post("/auth/forgot-password", json=forgot_data)
            results["auth_tests"]["forgot_password"] = {
                "status": "PASS" if response.status_code == 200 else "FAIL",
                "status_code": response.status_code,
                "response": response.json()
            }
            if response.status_code == 200:
                results["summary"]["passed"] += 1
                reset_token = response.json().get("reset_token")
            else:
                reset_token = None
            results["summary"]["total"] += 1
        except Exception as e:
            results["auth_tests"]["forgot_password"] = {"status": "ERROR", "error": str(e)}
            results["summary"]["failed"] += 1
            results["summary"]["total"] += 1
        
        # Test 6: Reset password (if token available)
        if reset_token:
            try:
                reset_data = {
                    "token": reset_token,
                    "new_password": "newpassword123"
                }
                response = client.post("/auth/reset-password", json=reset_data)
                results["auth_tests"]["reset_password"] = {
                    "status": "PASS" if response.status_code == 200 else "FAIL",
                    "status_code": response.status_code,
                    "response": response.json()
                }
                if response.status_code == 200:
                    results["summary"]["passed"] += 1
                else:
                    results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
            except Exception as e:
                results["auth_tests"]["reset_password"] = {"status": "ERROR", "error": str(e)}
                results["summary"]["failed"] += 1
                results["summary"]["total"] += 1
        
        return results
        
    except Exception as e:
        return {"error": f"Test execution failed: {str(e)}"}


@router.get("/health-check")
def health_check():
    """Simple health check for testing."""
    return {
        "status": "ok",
        "message": "Testing endpoints are working",
        "available_tests": [
            "POST /test/run-all - Run comprehensive API tests",
            "GET /test/health-check - Simple health check"
        ]
    }


@router.post("/cleanup")
def cleanup_test_data(db: Session = Depends(get_db)):
    """Clean up test data from database."""
    try:
        # Delete test users
        test_users = db.query(User).filter(User.email.like("%test%")).all()
        for user in test_users:
            db.delete(user)
        db.commit()
        
        return {
            "message": "Test data cleaned up successfully",
            "deleted_users": len(test_users)
        }
    except Exception as e:
        return {"error": f"Cleanup failed: {str(e)}"}
