import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.users.models import User
from app.groups.models import Group, GroupMember, InvitationToken, Club
from app.core.security import get_password_hash
import json


class TestGroupManagement:
    """Test group creation, management, and member operations."""

    def test_create_group_success(self, client: TestClient, auth_headers: dict):
        """Test successful group creation."""
        response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "A test group"},
            headers=auth_headers
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Group"
        assert data["description"] == "A test group"
        assert "id" in data
        assert "creator_id" in data

    def test_create_group_limit(self, client: TestClient, auth_headers: dict, db: Session):
        """Test group creation limit (max 2 per user)."""
        # Create first group
        response1 = client.post(
            "/groups",
            json={"name": "Group 1", "description": "First group"},
            headers=auth_headers
        )
        assert response1.status_code == 201

        # Create second group
        response2 = client.post(
            "/groups",
            json={"name": "Group 2", "description": "Second group"},
            headers=auth_headers
        )
        assert response2.status_code == 201

        # Try to create third group (should fail)
        response3 = client.post(
            "/groups",
            json={"name": "Group 3", "description": "Third group"},
            headers=auth_headers
        )
        assert response3.status_code == 400
        assert "Group creation limit reached" in response3.json()["detail"]

    def test_list_my_groups(self, client: TestClient, auth_headers: dict, db: Session):
        """Test listing user's groups."""
        # Create a group
        response = client.post(
            "/groups",
            json={"name": "My Group", "description": "My test group"},
            headers=auth_headers
        )
        assert response.status_code == 201

        # List groups
        response = client.get("/groups", headers=auth_headers)
        assert response.status_code == 200
        groups = response.json()
        assert len(groups) == 1
        assert groups[0]["name"] == "My Group"

    def test_get_group_details(self, client: TestClient, auth_headers: dict, db: Session):
        """Test getting group details."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test description"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Get group details
        response = client.get(f"/groups/{group_id}", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Group"
        assert data["description"] == "Test description"

    def test_get_group_details_not_member(self, client: TestClient, auth_headers: dict, db: Session):
        """Test getting group details when not a member."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Try to access group as different user
        response = client.get(f"/groups/{other_group.id}", headers=auth_headers)
        assert response.status_code == 403
        assert "Not a member" in response.json()["detail"]

    def test_delete_group_creator(self, client: TestClient, auth_headers: dict, db: Session):
        """Test group deletion by creator."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "To Delete", "description": "Will be deleted"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Delete group
        response = client.delete(f"/groups/{group_id}", headers=auth_headers)
        assert response.status_code == 200
        assert "deleted successfully" in response.json()["message"]

        # Verify group is deleted
        response = client.get(f"/groups/{group_id}", headers=auth_headers)
        assert response.status_code == 404

    def test_delete_group_not_creator_or_admin(self, client: TestClient, auth_headers: dict, db: Session):
        """Test group deletion by non-creator/non-admin."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Try to delete group as different user
        response = client.delete(f"/groups/{other_group.id}", headers=auth_headers)
        assert response.status_code == 403
        assert "Only creator or admin can delete group" in response.json()["detail"]


class TestGroupMembers:
    """Test group member management."""

    def test_get_group_members(self, client: TestClient, auth_headers: dict, db: Session):
        """Test listing group members."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Get members
        response = client.get(f"/groups/{group_id}/members", headers=auth_headers)
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 1  # Creator is automatically added as admin
        assert members[0]["is_admin"] == True

    def test_get_group_members_not_member(self, client: TestClient, auth_headers: dict, db: Session):
        """Test getting group members when not a member."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Try to get members as different user
        response = client.get(f"/groups/{other_group.id}/members", headers=auth_headers)
        assert response.status_code == 403
        assert "Not a member of this group" in response.json()["detail"]

    def test_add_admin(self, client: TestClient, auth_headers: dict, db: Session):
        """Test adding admin to group."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create another user
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        # Add as admin
        response = client.post(
            f"/groups/{group_id}/admins/{other_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == other_user.id
        assert data["is_admin"] == True

    def test_add_admin_not_admin(self, client: TestClient, auth_headers: dict, db: Session):
        """Test adding admin when requester is not admin."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Add current user as member (not admin)
        # Use the authenticated user's ID via token owner
        # Fetch current user profile to get ID
        profile = client.get("/users/profile", headers=auth_headers)
        current_user_id = profile.json()["id"]
        member = GroupMember(group_id=other_group.id, user_id=current_user_id, is_admin=False)
        db.add(member)
        db.commit()

        # Try to add admin as non-admin member
        response = client.post(
            f"/groups/{other_group.id}/admins/{other_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_remove_member(self, client: TestClient, auth_headers: dict, db: Session):
        """Test removing member from group."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create another user and add as member
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        member = GroupMember(group_id=group_id, user_id=other_user.id, is_admin=False)
        db.add(member)
        db.commit()

        # Remove member
        response = client.delete(
            f"/groups/{group_id}/members/{other_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200
        assert "removed successfully" in response.json()["message"]

    def test_remove_creator(self, client: TestClient, auth_headers: dict, db: Session):
        """Test removing group creator (should fail)."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Try to remove creator
        response = client.delete(
            f"/groups/{group_id}/members/1",  # Assuming user ID is 1
            headers=auth_headers
        )
        assert response.status_code == 400
        assert "Cannot remove group creator" in response.json()["detail"]

    def test_leave_group(self, client: TestClient, auth_headers: dict, db: Session):
        """Test leaving group."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Add current user as member
        profile = client.get("/users/profile", headers=auth_headers)
        current_user_id = profile.json()["id"]
        member = GroupMember(group_id=other_group.id, user_id=current_user_id, is_admin=False)
        db.add(member)
        db.commit()

        # Leave group
        response = client.delete(f"/groups/{other_group.id}/leave", headers=auth_headers)
        assert response.status_code == 200
        assert "Left group successfully" in response.json()["message"]

    def test_leave_group_as_creator(self, client: TestClient, auth_headers: dict, db: Session):
        """Test leaving group as creator (should fail)."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Try to leave as creator
        response = client.delete(f"/groups/{group_id}/leave", headers=auth_headers)
        assert response.status_code == 400
        assert "Creator cannot leave group" in response.json()["detail"]


class TestInvitations:
    """Test group invitation system."""

    def test_create_invite_token(self, client: TestClient, auth_headers: dict, db: Session):
        """Test creating invitation token."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create invite token
        response = client.post(
            f"/groups/{group_id}/invites",
            json={"expires_in_minutes": 60},
            headers=auth_headers
        )
        assert response.status_code == 200
        data = response.json()
        assert "token" in data
        assert data["group_id"] == group_id
        assert data["is_revoked"] == False

    def test_create_invite_token_not_admin(self, client: TestClient, auth_headers: dict, db: Session):
        """Test creating invite token when not admin."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Add current user as member (not admin)
        profile = client.get("/users/profile", headers=auth_headers)
        current_user_id = profile.json()["id"]
        member = GroupMember(group_id=other_group.id, user_id=current_user_id, is_admin=False)
        db.add(member)
        db.commit()

        # Try to create invite token
        response = client.post(
            f"/groups/{other_group.id}/invites",
            json={"expires_in_minutes": 60},
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]

    def test_create_invite_token_forbidden_non_member(self, client: TestClient, auth_headers: dict, db: Session):
        """Non-members cannot create invites."""
        # Another user creates a group
        other_user = User(
            email="someother@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other"
        )
        db.add(other_user)
        db.commit()
        group = Group(name="Foreign Group", creator_id=other_user.id)
        db.add(group)
        db.commit()
        # Current user not a member
        r = client.post(f"/groups/{group.id}/invites", json={"expires_in_minutes": 10}, headers=auth_headers)
        assert r.status_code == 403

    def test_join_group_with_token(self, client: TestClient, auth_headers: dict, db: Session):
        """Test joining group with valid token."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create invite token
        invite_response = client.post(
            f"/groups/{group_id}/invites",
            json={"expires_in_minutes": 60},
            headers=auth_headers
        )
        token = invite_response.json()["token"]

        # Create another user to join
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        # Login as other user
        login_response = client.post(
            "/auth/login",
            json={"email": "other@test.com", "password": "password123"}
        )
        other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        # Join with token
        response = client.post(f"/groups/join/{token}", headers=other_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["group_id"] == group_id
        assert data["is_admin"] == False

    def test_join_group_with_expired_token(self, client: TestClient, auth_headers: dict, db: Session):
        """Joining with expired token should fail."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Expire Group", "description": "Test group"},
            headers=auth_headers
        )
        gid = create_response.json()["id"]
        # Create very short-lived invite
        invite = client.post(f"/groups/{gid}/invites", json={"expires_in_minutes": 1}, headers=auth_headers)
        assert invite.status_code == 200
        token = invite.json()["token"]
        # Simulate expiry by directly manipulating DB
        inv_obj = db.query(InvitationToken).filter(InvitationToken.token == token).first()
        from datetime import datetime, timedelta
        inv_obj.expires_at = datetime.utcnow() - timedelta(minutes=1)
        db.add(inv_obj)
        db.commit()
        # Join should now fail
        r = client.post(f"/groups/join/{token}", headers=auth_headers)
        assert r.status_code == 400
        assert "expired" in r.json()["detail"].lower()

    def test_join_group_already_member(self, client: TestClient, auth_headers: dict, db: Session):
        """Test joining group when already a member."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create invite token
        invite_response = client.post(
            f"/groups/{group_id}/invites",
            json={"expires_in_minutes": 60},
            headers=auth_headers
        )
        token = invite_response.json()["token"]

        # Try to join with same user (already a member)
        response = client.post(f"/groups/join/{token}", headers=auth_headers)
        assert response.status_code == 400
        assert "already a member of this group" in response.json()["detail"]

    def test_join_group_invalid_token(self, client: TestClient, auth_headers: dict):
        """Test joining group with invalid token."""
        response = client.post("/groups/join/invalid_token", headers=auth_headers)
        assert response.status_code == 400
        assert "Invalid invite token" in response.json()["detail"]

    def test_revoke_invite_token(self, client: TestClient, auth_headers: dict, db: Session):
        """Test revoking invitation token."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create invite token
        invite_response = client.post(
            f"/groups/{group_id}/invites",
            json={"expires_in_minutes": 60},
            headers=auth_headers
        )
        token = invite_response.json()["token"]

        # Revoke token
        response = client.post(f"/groups/invites/{token}/revoke", headers=auth_headers)
        assert response.status_code == 200
        data = response.json()
        assert data["is_revoked"] == True

        # Try to join with revoked token
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        login_response = client.post(
            "/auth/login",
            json={"email": "other@test.com", "password": "password123"}
        )
        other_headers = {"Authorization": f"Bearer {login_response.json()['access_token']}"}

        join_response = client.post(f"/groups/join/{token}", headers=other_headers)
        assert join_response.status_code == 400
        assert "Invalid invite token" in join_response.json()["detail"]


class TestClubs:
    """Test club management and 365scores integration."""

    def test_fetch_clubs(self, client: TestClient, auth_headers: dict):
        """Test fetching clubs from 365scores API."""
        response = client.get("/groups/clubs", headers=auth_headers)
        assert response.status_code == 200
        clubs = response.json()
        assert isinstance(clubs, list)
        # Note: This test might fail if 365scores API is down
        # In that case, it should return empty list or cached data

    def test_fetch_clubs_unauthorized(self, client: TestClient):
        """Test fetching clubs without authentication."""
        response = client.get("/groups/clubs")
        assert response.status_code == 401


class TestGroupPermissions:
    """Test group permission system."""

    def test_member_can_see_members(self, client: TestClient, auth_headers: dict, db: Session):
        """Test that group members can see member list."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Get members as creator
        response = client.get(f"/groups/{group_id}/members", headers=auth_headers)
        assert response.status_code == 200
        members = response.json()
        assert len(members) == 1
        assert members[0]["is_admin"] == True
        # user_name should be populated
        assert "user_name" in members[0]

    def test_non_member_cannot_see_members(self, client: TestClient, auth_headers: dict, db: Session):
        """Test that non-members cannot see member list."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Try to get members as non-member
        response = client.get(f"/groups/{other_group.id}/members", headers=auth_headers)
        assert response.status_code == 403
        assert "Not a member of this group" in response.json()["detail"]

    def test_admin_can_manage_members(self, client: TestClient, auth_headers: dict, db: Session):
        """Test that admins can manage members."""
        # Create a group
        create_response = client.post(
            "/groups",
            json={"name": "Test Group", "description": "Test group"},
            headers=auth_headers
        )
        group_id = create_response.json()["id"]

        # Create another user
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        # Add as member
        member = GroupMember(group_id=group_id, user_id=other_user.id, is_admin=False)
        db.add(member)
        db.commit()

        # Remove member as admin
        response = client.delete(
            f"/groups/{group_id}/members/{other_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 200

    def test_non_admin_cannot_manage_members(self, client: TestClient, auth_headers: dict, db: Session):
        """Test that non-admins cannot manage members."""
        # Create another user and group
        other_user = User(
            email="other@test.com",
            hashed_password=get_password_hash("password123"),
            name="Other User"
        )
        db.add(other_user)
        db.commit()

        other_group = Group(name="Other Group", creator_id=other_user.id)
        db.add(other_group)
        db.commit()

        # Add current user as member (not admin)
        profile = client.get("/users/profile", headers=auth_headers)
        current_user_id = profile.json()["id"]
        member = GroupMember(group_id=other_group.id, user_id=current_user_id, is_admin=False)
        db.add(member)
        db.commit()

        # Try to remove another member as non-admin
        third_user = User(
            email="third@test.com",
            hashed_password=get_password_hash("password123"),
            name="Third User"
        )
        db.add(third_user)
        db.commit()

        third_member = GroupMember(group_id=other_group.id, user_id=third_user.id, is_admin=False)
        db.add(third_member)
        db.commit()

        response = client.delete(
            f"/groups/{other_group.id}/members/{third_user.id}",
            headers=auth_headers
        )
        assert response.status_code == 403
        assert "Admin access required" in response.json()["detail"]
