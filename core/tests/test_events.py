import pytest
from rest_framework import status

from core.models import Event


@pytest.mark.django_db
class TestEvents:

    def test_admin_can_create_event(self, client_admin, event_data):
        response = client_admin.post("/api/events/", event_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Shea Stadium"
        assert Event.objects.count() == 1

    def test_odie_cannot_create_event(self, client_odie, event_data):
        response = client_odie.post("/api/events/", event_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Event.objects.count() == 0

    def test_unauthenticated_cannot_access_events(self, client):
        response = client.get("/api/events/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_odie_can_list_events(self, client_admin, client_odie, event_data):
        client_admin.post("/api/events/", event_data)
        response = client_odie.get("/api/events/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_odie_can_retrieve_event(self, client_admin, client_odie, event_data):
        create_response = client_admin.post("/api/events/", event_data)
        event_id = create_response.data["id"]
        response = client_odie.get(f"/api/events/{event_id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Shea Stadium"

    def test_admin_can_update_event(self, client_admin, event_data):
        create_response = client_admin.post("/api/events/", event_data)
        event_id = create_response.data["id"]
        response = client_admin.patch(
            f"/api/events/{event_id}/",
            {"status": "confirmed"},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["status"] == "confirmed"

    def test_odie_cannot_update_event(self, client_admin, client_odie, event_data):
        create_response = client_admin.post("/api/events/", event_data)
        event_id = create_response.data["id"]
        response = client_odie.patch(
            f"/api/events/{event_id}/",
            {"status": "confirmed"},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_event(self, client_admin, event_data):
        create_response = client_admin.post("/api/events/", event_data)
        event_id = create_response.data["id"]
        response = client_admin.delete(f"/api/events/{event_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Event.objects.count() == 0

    def test_odie_cannot_delete_event(self, client_admin, client_odie, event_data):
        create_response = client_admin.post("/api/events/", event_data)
        event_id = create_response.data["id"]
        response = client_odie.delete(f"/api/events/{event_id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Event.objects.count() == 1

    def test_create_event_with_invalid_type(self, client_admin, event_data):
        bad_data = {**event_data, "type": "concert"}
        response = client_admin.post("/api/events/", bad_data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_create_event_missing_required_field(self, client_admin):
        response = client_admin.post("/api/events/", {"title": "Incomplete"})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
