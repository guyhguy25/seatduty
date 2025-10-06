import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User
from app.security import decode_token


class TestAuth:
    """Test authentication endpoints."""

    def test_register_success(self, client: TestClient, db_session: Session):
        """Test successful user registration."""
        response = client.post("/auth/register", json={
            "email": "newuser@example.com",
            "password": "newpassword123",
            "name": "New User",
            "phone": "9876543210"
        })
        
        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@example.com"
        assert data["name"] == "New User"
        assert data["phone"] == "9876543210"
        assert "id" in data
        assert "hashed_password" not in data

    def test_register_duplicate_email(self, client: TestClient, test_user):
        """Test registration with duplicate email."""
        response = client.post("/auth/register", json={
            "email": "test@example.com",
            "password": "password123",
            "name": "Another User"
        })
        
        assert response.status_code == 409
        assert "Email already registered" in response.json()["detail"]

    def test_register_invalid_email(self, client: TestClient):
        """Test registration with invalid email."""
        response = client.post("/auth/register", json={
            "email": "invalid-email",
            "password": "password123",
            "name": "Test User"
        })
        
        assert response.status_code == 422

    def test_register_short_password(self, client: TestClient):
        """Test registration with short password."""
        response = client.post("/auth/register", json={
            "email": "user@example.com",
            "password": "123",
            "name": "Test User"
        })
        
        assert response.status_code == 422

    def test_login_success(self, client: TestClient, test_user):
        """Test successful login."""
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_invalid_credentials(self, client: TestClient, test_user):
        """Test login with invalid credentials."""
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "wrongpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_login_nonexistent_user(self, client: TestClient):
        """Test login with nonexistent user."""
        response = client.post("/auth/login", json={
            "email": "nonexistent@example.com",
            "password": "password123"
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_refresh_token_success(self, client: TestClient, test_user):
        """Test successful token refresh."""
        # First login to get tokens
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Use refresh token
        response = client.post("/auth/refresh", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_refresh_token_invalid(self, client: TestClient):
        """Test refresh with invalid token."""
        response = client.post("/auth/refresh", json={
            "refresh_token": "invalid_token"
        })
        
        assert response.status_code == 401
        assert "Invalid refresh token" in response.json()["detail"]

    def test_logout_success(self, client: TestClient, test_user):
        """Test successful logout."""
        # First login to get refresh token
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        refresh_token = login_response.json()["refresh_token"]
        
        # Logout
        response = client.post("/auth/logout", json={
            "refresh_token": refresh_token
        })
        
        assert response.status_code == 200
        assert "Logged out successfully" in response.json()["message"]

    def test_forgot_password_success(self, client: TestClient, test_user):
        """Test successful forgot password."""
        response = client.post("/auth/forgot-password", json={
            "email": "test@example.com"
        })
        
        assert response.status_code == 200
        data = response.json()
        assert "reset_token" in data
        assert "expires_in" in data

    def test_forgot_password_nonexistent_user(self, client: TestClient):
        """Test forgot password with nonexistent user."""
        response = client.post("/auth/forgot-password", json={
            "email": "nonexistent@example.com"
        })
        
        assert response.status_code == 200
        # Should not reveal if user exists
        assert "reset_token" not in response.json()

    def test_reset_password_success(self, client: TestClient, test_user):
        """Test successful password reset."""
        # First get reset token
        forgot_response = client.post("/auth/forgot-password", json={
            "email": "test@example.com"
        })
        reset_token = forgot_response.json()["reset_token"]
        
        # Reset password
        response = client.post("/auth/reset-password", json={
            "token": reset_token,
            "new_password": "newpassword123"
        })
        
        assert response.status_code == 200
        assert "Password reset successfully" in response.json()["message"]

    def test_reset_password_invalid_token(self, client: TestClient):
        """Test reset password with invalid token."""
        response = client.post("/auth/reset-password", json={
            "token": "invalid_token",
            "new_password": "newpassword123"
        })
        
        assert response.status_code == 400
        assert "Invalid reset token" in response.json()["detail"]

    def test_reset_password_short_password(self, client: TestClient, test_user):
        """Test reset password with short password."""
        # First get reset token
        forgot_response = client.post("/auth/forgot-password", json={
            "email": "test@example.com"
        })
        reset_token = forgot_response.json()["reset_token"]
        
        # Reset password with short password
        response = client.post("/auth/reset-password", json={
            "token": reset_token,
            "new_password": "123"
        })
        
        assert response.status_code == 422

    def test_jwt_token_structure(self, client: TestClient, test_user):
        """Test JWT token structure and content."""
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        
        access_token = response.json()["access_token"]
        token_data = decode_token(access_token)
        
        assert token_data is not None
        assert token_data["sub"] == str(test_user.id)
        assert token_data["type"] == "access"
        assert "exp" in token_data
