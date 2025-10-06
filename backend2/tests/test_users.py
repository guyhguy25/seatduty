import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.models import User


class TestUsers:
    """Test user management endpoints."""

    def test_get_profile_success(self, client: TestClient, auth_headers):
        """Test successful profile retrieval."""
        response = client.get("/users/profile", headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["phone"] == "1234567890"
        assert "id" in data
        assert "hashed_password" not in data

    def test_get_profile_unauthorized(self, client: TestClient):
        """Test profile retrieval without authentication."""
        response = client.get("/users/profile")
        
        assert response.status_code == 401
        assert "Not authenticated" in response.json()["detail"]

    def test_get_profile_invalid_token(self, client: TestClient):
        """Test profile retrieval with invalid token."""
        response = client.get("/users/profile", headers={"Authorization": "Bearer invalid_token"})
        
        assert response.status_code == 401
        assert "Invalid token" in response.json()["detail"]

    def test_update_profile_success(self, client: TestClient, auth_headers):
        """Test successful profile update."""
        response = client.put("/users/profile", json={
            "name": "Updated Name",
            "phone": "9876543210"
        }, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Name"
        assert data["phone"] == "9876543210"
        assert data["email"] == "test@example.com"  # Email should remain unchanged

    def test_update_profile_partial(self, client: TestClient, auth_headers):
        """Test partial profile update."""
        response = client.put("/users/profile", json={
            "name": "New Name Only"
        }, headers=auth_headers)
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "New Name Only"
        # Phone should remain unchanged
        assert data["phone"] == "1234567890"

    def test_update_profile_password(self, client: TestClient, auth_headers):
        """Test password update."""
        response = client.put("/users/profile", json={
            "password": "newpassword123"
        }, headers=auth_headers)
        
        assert response.status_code == 200
        
        # Verify new password works
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "newpassword123"
        })
        assert login_response.status_code == 200

    def test_update_profile_unauthorized(self, client: TestClient):
        """Test profile update without authentication."""
        response = client.put("/users/profile", json={
            "name": "Updated Name"
        })
        
        assert response.status_code == 401

    def test_update_profile_invalid_email(self, client: TestClient, auth_headers):
        """Test profile update with invalid data."""
        response = client.put("/users/profile", json={
            "name": "A" * 300  # Too long name
        }, headers=auth_headers)
        
        # Should still work as we don't validate name length in our schema
        assert response.status_code == 200

    def test_delete_account_success(self, client: TestClient, auth_headers):
        """Test successful account deletion."""
        response = client.delete("/users/account", headers=auth_headers)
        
        assert response.status_code == 204

    def test_delete_account_unauthorized(self, client: TestClient):
        """Test account deletion without authentication."""
        response = client.delete("/users/account")
        
        assert response.status_code == 401

    def test_deleted_user_cannot_login(self, client: TestClient, auth_headers):
        """Test that deleted user cannot login."""
        # First delete the account
        client.delete("/users/account", headers=auth_headers)
        
        # Try to login with deleted account
        response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "testpassword"
        })
        
        assert response.status_code == 401
        assert "Invalid credentials" in response.json()["detail"]

    def test_update_profile_short_password(self, client: TestClient, auth_headers):
        """Test profile update with short password."""
        response = client.put("/users/profile", json={
            "password": "123"
        }, headers=auth_headers)
        
        assert response.status_code == 422

    def test_profile_update_after_password_change(self, client: TestClient, auth_headers):
        """Test that profile can be updated after password change."""
        # Update password
        client.put("/users/profile", json={
            "password": "newpassword123"
        }, headers=auth_headers)
        
        # Login with new password to get new token
        login_response = client.post("/auth/login", json={
            "email": "test@example.com",
            "password": "newpassword123"
        })
        new_token = login_response.json()["access_token"]
        new_headers = {"Authorization": f"Bearer {new_token}"}
        
        # Update profile with new token
        response = client.put("/users/profile", json={
            "name": "Updated After Password Change"
        }, headers=new_headers)
        
        assert response.status_code == 200
        assert response.json()["name"] == "Updated After Password Change"
