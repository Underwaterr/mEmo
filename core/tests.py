from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import User, Event, Poll


class PollAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="garfield",
            password="simple-password",
            display_name="Garf",
            is_staff=True
        )

        self.member = User.objects.create_user(
            username="odie",
            password="whatever-man",
            display_name="Odie",
            is_staff=False
        )

        self.poll_data = {
            "title": "Shea Stadium"
        }

    def test_admin_can_create_poll(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/polls/", self.poll_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Shea Stadium")
        self.assertEqual(Poll.objects.count(), 1)

    def test_member_cannot_create_poll(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post("/api/polls/", self.poll_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Poll.objects.count(), 0)

    def test_unauthenticated_cannot_access_polls(self):
        response = self.client.get("/api/polls/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_list_polls(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post("/api/polls/", self.poll_data)

        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/polls/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_member_can_retrieve_poll(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/polls/", self.poll_data)
        poll_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.get(f"/api/polls/{poll_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Shea Stadium")

    def test_admin_can_update_poll(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/polls/", self.poll_data)
        poll_id = create_response.data["id"]

        response = self.client.patch(
            f"/api/polls/{poll_id}/",
            {"closed": True},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["closed"], True)

    def test_member_cannot_update_poll(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/polls/", self.poll_data)
        poll_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f"/api/polls/{poll_id}/",
            {"closed": True},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_poll(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/polls/", self.poll_data)
        poll_id = create_response.data["id"]

        response = self.client.delete(f"/api/polls/{poll_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Poll.objects.count(), 0)

    def test_member_cannot_delete_poll(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/polls/", self.poll_data)
        poll_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.delete(f"/api/polls/{poll_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Poll.objects.count(), 1)

    def test_create_poll_missing_required_field(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/polls/", {"closed": True})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

class EventAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="garfield",
            password="simple-password",
            display_name="Garf",
            is_staff=True
        )
        self.member = User.objects.create_user(
            username="odie",
            password="whatever-man",
            display_name="Odie",
            is_staff=False
        )
        self.event_data = {
            "title": "Shea Stadium",
            "type": "gig",
            "date": "2026-05-15",
            "status": "pending"
        }

    def test_admin_can_create_event(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/events/", self.event_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["title"], "Shea Stadium")
        self.assertEqual(Event.objects.count(), 1)

    def test_member_cannot_create_event(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post("/api/events/", self.event_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 0)

    def test_unauthenticated_cannot_access_events(self):
        response = self.client.get("/api/events/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_list_events(self):
        self.client.force_authenticate(user=self.admin)
        self.client.post("/api/events/", self.event_data)

        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/events/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_member_can_retrieve_event(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/events/", self.event_data)
        event_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.get(f"/api/events/{event_id}/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["title"], "Shea Stadium")

    def test_admin_can_update_event(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/events/", self.event_data)
        event_id = create_response.data["id"]

        response = self.client.patch(
            f"/api/events/{event_id}/",
            {"status": "confirmed"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["status"], "confirmed")

    def test_member_cannot_update_event(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/events/", self.event_data)
        event_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f"/api/events/{event_id}/",
            {"status": "confirmed"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_event(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/events/", self.event_data)
        event_id = create_response.data["id"]

        response = self.client.delete(f"/api/events/{event_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Event.objects.count(), 0)

    def test_member_cannot_delete_event(self):
        self.client.force_authenticate(user=self.admin)
        create_response = self.client.post("/api/events/", self.event_data)
        event_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.delete(f"/api/events/{event_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Event.objects.count(), 1)

    def test_create_event_with_invalid_type(self):
        self.client.force_authenticate(user=self.admin)
        bad_data = {**self.event_data, "type": "concert"}
        response = self.client.post("/api/events/", bad_data)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_create_event_missing_required_field(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/events/", {"title": "Incomplete"})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
