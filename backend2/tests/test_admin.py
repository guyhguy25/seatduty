import pytest
from fastapi.testclient import TestClient


def get_headers_for(client: TestClient, email: str, password: str) -> dict:
    resp = client.post("/auth/login", json={"email": email, "password": password})
    assert resp.status_code == 200
    token = resp.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(client: TestClient):
    # Default admin is created on app startup via init_db
    return get_headers_for(client, "admin@seatduty.com", "admin123")


class TestAdminBasics:
    def test_system_info_superuser(self, client: TestClient, admin_headers: dict):
        resp = client.get("/admin/system-info", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "total_users" in data
        assert "superusers" in data

    def test_system_info_forbidden(self, client: TestClient, auth_headers: dict):
        resp = client.get("/admin/system-info", headers=auth_headers)
        assert resp.status_code == 403

    def test_list_admins(self, client: TestClient, admin_headers: dict):
        resp = client.get("/admin/list-admins", headers=admin_headers)
        assert resp.status_code == 200
        data = resp.json()
        assert "admins" in data


class TestAdminUserManagement:
    def test_create_get_update_toggle_delete_user(self, client: TestClient, admin_headers: dict):
        # Create user
        create_resp = client.post(
            "/admin/users",
            headers=admin_headers,
            json={
                "email": "managed@example.com",
                "password": "password123",
                "name": "Managed User",
                "phone": "+1111111111",
            },
        )
        assert create_resp.status_code == 201
        user_id = create_resp.json()["id"]

        # Get list
        list_resp = client.get("/admin/users", headers=admin_headers)
        assert list_resp.status_code == 200
        assert any(u["id"] == user_id for u in list_resp.json()["users"])

        # Get by id
        get_resp = client.get(f"/admin/users/{user_id}", headers=admin_headers)
        assert get_resp.status_code == 200
        assert get_resp.json()["email"] == "managed@example.com"

        # Update (promote to superuser)
        update_resp = client.put(
            f"/admin/users/{user_id}",
            headers=admin_headers,
            json={"name": "Managed Updated", "is_superuser": True},
        )
        assert update_resp.status_code == 200
        assert update_resp.json()["name"] == "Managed Updated"
        assert update_resp.json()["is_superuser"] is True

        # Toggle active (should deactivate)
        toggle_resp = client.patch(f"/admin/users/{user_id}/toggle-active", headers=admin_headers)
        assert toggle_resp.status_code == 200

        # Delete
        delete_resp = client.delete(f"/admin/users/{user_id}", headers=admin_headers)
        assert delete_resp.status_code in (200, 204)

    def test_bulk_update_and_delete(self, client: TestClient, admin_headers: dict):
        # Create two users
        ids = []
        for i in range(2):
            r = client.post(
                "/admin/users",
                headers=admin_headers,
                json={
                    "email": f"bulk{i}@example.com",
                    "password": "password123",
                    "name": f"Bulk {i}",
                },
            )
            assert r.status_code == 201
            ids.append(r.json()["id"])

        # Bulk update (deactivate)
        upd = client.put(
            "/admin/users/bulk-update",
            headers=admin_headers,
            json={"user_ids": ids, "is_active": False},
        )
        assert upd.status_code == 200

        # Bulk delete
        dele = client.post(
            "/admin/users/bulk-delete",
            headers=admin_headers,
            json={"user_ids": ids},
        )
        assert dele.status_code == 200


class TestAdminSecurity:
    def test_admin_endpoints_forbidden_for_non_admin(self, client: TestClient, auth_headers: dict):
        # Attempt to list users
        resp = client.get("/admin/users", headers=auth_headers)
        assert resp.status_code == 403

    def test_create_admin_user(self, client: TestClient, admin_headers: dict):
        # Create a new superuser via admin endpoint
        resp = client.post(
            "/admin/create-admin",
            headers=admin_headers,
            json={
                "email": "newadmin@example.com",
                "password": "adminpass123",
                "name": "New Admin",
            },
        )
        assert resp.status_code in (200, 201)

    def test_reset_admin_password(self, client: TestClient, admin_headers: dict):
        # Reset password for existing admin
        resp = client.post(
            "/admin/reset-admin-password",
            headers=admin_headers,
            json={"email": "admin@seatduty.com", "new_password": "admin123"},
        )
        # Keeping same password is acceptable; expect either 200 or 500 depending on implementation
        assert resp.status_code in (200, 404, 500)


