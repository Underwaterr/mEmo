import pytest
from rest_framework import status

from core.models import User


@pytest.mark.django_db
class TestAuthentication:

    def test_login_with_valid_credentials(self, client, admin):
        response = client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "password"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "garfield"
        assert response.data["display_name"] == "Garf"
        assert response.data["is_staff"] == True

    def test_login_returns_user_id(self, client, admin):
        response = client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "password"},
        )
        assert response.data["id"] == str(admin.id)

    def test_login_with_wrong_password(self, client, admin):
        response = client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "wrongpassword"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_with_nonexistent_user(self, client, admin):
        response = client.post(
            "/api/auth/login/",
            {"username": "nobody", "password": "password"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_missing_fields(self, client):
        response = client.post("/api/auth/login/", {})
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_login_creates_session(self, client, jon):
        client.post(
            "/api/auth/login/",
            {"username": "arbuckle77", "password": "cool-guy-alert"},
        )
        response = client.get("/api/auth/check/")
        assert response.status_code ==  status.HTTP_200_OK
        assert response.data["username"] == "arbuckle77"

    def test_logout(self, client, odie):
        client.post(
            "/api/auth/login/",
            {"username": "odie", "password": "password2"},
        )
        response = client.post("/api/auth/logout/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_logout_destroys_session(self, client, odie):
        client.post(
            "/api/auth/login/",
            {"username": "odie", "password": "password2"},
        )
        client.post("/api/auth/logout/")
        response = client.get("/api/auth/check/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_logout_requires_authentication(self, client):
        response = client.post("/api/auth/logout/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_check_auth_when_authenticated(self, client, odie):
        client.force_authenticate(user=odie)
        response = client.get("/api/auth/check/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["username"] == "odie"
        assert response.data["display_name"] == "Odie"
        assert response.data["is_staff"] == False

    def test_check_auth_when_not_authenticated(self, client):
        response = client.get("/api/auth/check/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_login_does_not_expose_password(self, client, admin):
        response = client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "password"},
        )
        assert "password" not in response.data

    def test_check_auth_does_not_expose_password(self, client, admin):
        client.force_authenticate(user=admin)
        response = client.get("/api/auth/check/")
        assert "password" not in response.data

    def test_inactive_user_cannot_login(self, client):
        inactive = User.objects.create_user(
            username="inactive",
            password="omgnoway",
            display_name="Ghost",
            is_active=False,
        )
        response = client.post(
            "/api/auth/login/",
            {"username": "inactive", "password": "omgnoway"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
