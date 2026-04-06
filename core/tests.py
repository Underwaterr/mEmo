from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient

from .models import User, Event, Poll, PollInvitation, PollDate, PollResponse


class AuthAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="garfield",
            password="password",
            display_name="Garf",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="lyman",
            password="who-is-he",
            display_name="Lyman",
            is_staff=False,
        )

    def test_login_with_valid_credentials(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "password"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "garfield")
        self.assertEqual(response.data["display_name"], "Garf")
        self.assertEqual(response.data["is_staff"], True)

    def test_login_returns_user_id(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "password"},
        )
        self.assertEqual(response.data["id"], str(self.admin.id))

    def test_login_with_wrong_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "wrongpassword"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_with_nonexistent_user(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "nobody", "password": "password"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_missing_fields(self):
        response = self.client.post("/api/auth/login/", {})
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_login_creates_session(self):
        self.client.post(
            "/api/auth/login/",
            {"username": "lyman", "password": "who-is-he"},
        )
        response = self.client.get("/api/auth/check/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "lyman")

    def test_logout(self):
        self.client.post(
            "/api/auth/login/",
            {"username": "lyman", "password": "who-is-he"},
        )
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_logout_destroys_session(self):
        self.client.post(
            "/api/auth/login/",
            {"username": "lyman", "password": "who-is-he"},
        )
        self.client.post("/api/auth/logout/")
        response = self.client.get("/api/auth/check/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_logout_requires_authentication(self):
        response = self.client.post("/api/auth/logout/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_check_auth_when_authenticated(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.get("/api/auth/check/")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["username"], "lyman")
        self.assertEqual(response.data["display_name"], "Lyman")
        self.assertEqual(response.data["is_staff"], False)

    def test_check_auth_when_not_authenticated(self):
        response = self.client.get("/api/auth/check/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_login_does_not_expose_password(self):
        response = self.client.post(
            "/api/auth/login/",
            {"username": "garfield", "password": "password"},
        )
        self.assertNotIn("password", response.data)

    def test_check_auth_does_not_expose_password(self):
        self.client.force_authenticate(user=self.admin)
        response = self.client.get("/api/auth/check/")
        self.assertNotIn("password", response.data)

    def test_inactive_user_cannot_login(self):
        inactive = User.objects.create_user(
            username="inactive",
            password="omgnoway",
            display_name="Ghost",
            is_active=False,
        )
        response = self.client.post(
            "/api/auth/login/",
            {"username": "inactive", "password": "omgnoway"},
        )
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


class PollInvitationAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="garfield",
            password="password",
            display_name="Garf",
            is_staff=True,
        )
        self.arlene = User.objects.create_user(
            username="arlene",
            password="password2",
            display_name="Arlene",
            is_staff=False,
        )
        self.nermal = User.objects.create_user(
            username="nermal",
            password="password3",
            display_name="Cutie",
            is_staff=False,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/polls/", {"title": "June Dates"})
        self.poll_id = response.data["id"]
        self.invitations_url = f"/api/polls/{self.poll_id}/invitations/"

    def test_admin_can_invite_user(self):
        response = self.client.post(
            self.invitations_url,
            {"user": self.arlene.id},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(PollInvitation.objects.count(), 1)

    def test_admin_can_invite_multiple_users(self):
        self.client.post(self.invitations_url, {"user": self.arlene.id})
        self.client.post(self.invitations_url, {"user": self.nermal.id})
        self.assertEqual(PollInvitation.objects.count(), 2)

    def test_duplicate_invitation_rejected(self):
        self.client.post(self.invitations_url, {"user": self.arlene.id})
        response = self.client.post(
            self.invitations_url,
            {"user": self.arlene.id},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PollInvitation.objects.count(), 1)

    def test_member_cannot_invite(self):
        self.client.force_authenticate(user=self.arlene)
        response = self.client.post(
            self.invitations_url,
            {"user": self.nermal.id},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_list_invitations(self):
        self.client.post(self.invitations_url, {"user": self.arlene.id})

        self.client.force_authenticate(user=self.arlene)
        response = self.client.get(self.invitations_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_admin_can_delete_invitation(self):
        create_response = self.client.post(
            self.invitations_url,
            {"user": self.arlene.id},
        )
        invitation_id = create_response.data["id"]

        response = self.client.delete(
            f"{self.invitations_url}{invitation_id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PollInvitation.objects.count(), 0)

    def test_member_cannot_delete_invitation(self):
        create_response = self.client.post(
            self.invitations_url,
            {"user": self.arlene.id},
        )
        invitation_id = create_response.data["id"]

        self.client.force_authenticate(user=self.arlene)
        response = self.client.delete(
            f"{self.invitations_url}{invitation_id}/",
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PollInvitation.objects.count(), 1)

    def test_invitation_scoped_to_poll(self):
        self.client.post(self.invitations_url, {"user": self.arlene.id})

        # create a second poll
        response = self.client.post("/api/polls/", {"title": "July Dates"})
        other_poll_id = response.data["id"]

        # the second poll's invitations should be empty
        response = self.client.get(
            f"/api/polls/{other_poll_id}/invitations/",
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_invitation_to_nonexistent_poll_returns_404(self):
        fake_poll_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.post(
            f"/api/polls/{fake_poll_id}/invitations/",
            {"user": self.arlene.id},
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_unauthenticated_cannot_access_invitations(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.invitations_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PollDateAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="garfield",
            password="password",
            display_name="Garf",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="arbuckle",
            password="passwordy",
            display_name="John",
            is_staff=False,
        )

        self.client.force_authenticate(user=self.admin)
        response = self.client.post("/api/polls/", {"title": "June Dates"})
        self.poll_id = response.data["id"]
        self.dates_url = f"/api/polls/{self.poll_id}/date-options/"

        self.date_data = {
            "date": "2026-06-14",
            "start_time": "20:00:00",
        }

    def test_admin_can_create_date(self):
        response = self.client.post(self.dates_url, self.date_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["date"], "2026-06-14")
        self.assertEqual(response.data["start_time"], "20:00:00")
        self.assertEqual(PollDate.objects.count(), 1)

    def test_date_belongs_to_poll(self):
        response = self.client.post(self.dates_url, self.date_data)
        self.assertEqual(str(response.data["poll"]), self.poll_id)

    def test_date_without_start_time(self):
        response = self.client.post(self.dates_url, {"date": "2026-06-14"})
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsNone(response.data["start_time"])

    def test_admin_can_create_multiple_dates(self):
        self.client.post(self.dates_url, {"date": "2026-06-14"})
        self.client.post(self.dates_url, {"date": "2026-06-21"})
        self.client.post(self.dates_url, {"date": "2026-06-28"})
        self.assertEqual(PollDate.objects.count(), 3)

    def test_member_cannot_create_date(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(self.dates_url, self.date_data)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_list_dates(self):
        self.client.post(self.dates_url, self.date_data)

        self.client.force_authenticate(user=self.member)
        response = self.client.get(self.dates_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_dates_scoped_to_poll(self):
        self.client.post(self.dates_url, self.date_data)

        response = self.client.post("/api/polls/", {"title": "July Dates"})
        other_dates_url = f"/api/polls/{response.data['id']}/date-options/"

        response = self.client.get(other_dates_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_dates_ordered_by_date_and_time(self):
        self.client.post(self.dates_url, {"date": "2026-06-28"})
        self.client.post(self.dates_url, {"date": "2026-06-14", "start_time": "21:00:00"})
        self.client.post(self.dates_url, {"date": "2026-06-14", "start_time": "18:00:00"})

        response = self.client.get(self.dates_url)
        dates = [(d["date"], d["start_time"]) for d in response.data]
        self.assertEqual(dates, [
            ("2026-06-14", "18:00:00"),
            ("2026-06-14", "21:00:00"),
            ("2026-06-28", None),
        ])

    def test_admin_can_update_date(self):
        create_response = self.client.post(self.dates_url, self.date_data)
        date_id = create_response.data["id"]

        response = self.client.patch(
            f"{self.dates_url}{date_id}/",
            {"start_time": "21:00:00"},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["start_time"], "21:00:00")

    def test_member_cannot_update_date(self):
        create_response = self.client.post(self.dates_url, self.date_data)
        date_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.patch(
            f"{self.dates_url}{date_id}/",
            {"start_time": "21:00:00"},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_delete_date(self):
        create_response = self.client.post(self.dates_url, self.date_data)
        date_id = create_response.data["id"]

        response = self.client.delete(f"{self.dates_url}{date_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PollDate.objects.count(), 0)

    def test_member_cannot_delete_date(self):
        create_response = self.client.post(self.dates_url, self.date_data)
        date_id = create_response.data["id"]

        self.client.force_authenticate(user=self.member)
        response = self.client.delete(f"{self.dates_url}{date_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PollDate.objects.count(), 1)

    def test_nonexistent_poll_returns_404(self):
        fake_poll_id = "00000000-0000-0000-0000-000000000000"
        response = self.client.post(
            f"/api/polls/{fake_poll_id}/date-options/",
            self.date_data,
        )
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_missing_date_field_returns_400(self):
        response = self.client.post(
            self.dates_url,
            {"start_time": "20:00:00"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_access_dates(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.dates_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)


class PollResponseAPITest(TestCase):
    def setUp(self):
        self.client = APIClient()

        self.admin = User.objects.create_user(
            username="garfield",
            password="password",
            display_name="Garf",
            is_staff=True,
        )
        self.member = User.objects.create_user(
            username="pookie",
            password="best-bear",
            display_name="Pookie",
            is_staff=False,
        )
        self.other_member = User.objects.create_user(
            username="odie",
            password="wordswordswords",
            display_name="Odie",
            is_staff=False,
        )

        # create poll with two date options
        self.client.force_authenticate(user=self.admin)
        poll_response = self.client.post("/api/polls/", {"title": "June Dates"})
        self.poll_id = poll_response.data["id"]
        self.dates_url = f"/api/polls/{self.poll_id}/date-options/"
        self.responses_url = f"/api/polls/{self.poll_id}/responses/"

        date_response = self.client.post(self.dates_url, {"date": "2026-06-14"})
        self.date_id_1 = date_response.data["id"]

        date_response = self.client.post(self.dates_url, {"date": "2026-06-21"})
        self.date_id_2 = date_response.data["id"]

    def test_member_can_respond(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["available"], True)
        self.assertEqual(PollResponse.objects.count(), 1)

    def test_response_user_set_automatically(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        self.assertEqual(str(response.data["user"]), str(self.member.id))

    def test_member_can_respond_to_multiple_dates(self):
        self.client.force_authenticate(user=self.member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_2, "available": False},
        )
        self.assertEqual(PollResponse.objects.count(), 2)

    def test_multiple_members_can_respond_to_same_date(self):
        self.client.force_authenticate(user=self.member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )

        self.client.force_authenticate(user=self.other_member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": False},
        )
        self.assertEqual(PollResponse.objects.count(), 2)

    def test_duplicate_response_rejected(self):
        self.client.force_authenticate(user=self.member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": False},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(PollResponse.objects.count(), 1)

    def test_response_with_comment(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.responses_url,
            {
                "date_option": self.date_id_1,
                "available": False,
                "comment": "Dentist appointment until 5",
            },
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data["comment"], "Dentist appointment until 5")

    def test_member_can_update_own_response(self):
        self.client.force_authenticate(user=self.member)
        create_response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response_id = create_response.data["id"]

        response = self.client.patch(
            f"{self.responses_url}{response_id}/",
            {"available": False},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data["available"], False)

    def test_member_cannot_update_other_members_response(self):
        self.client.force_authenticate(user=self.member)
        create_response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response_id = create_response.data["id"]

        self.client.force_authenticate(user=self.other_member)
        response = self.client.patch(
            f"{self.responses_url}{response_id}/",
            {"available": False},
        )
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_member_can_delete_own_response(self):
        self.client.force_authenticate(user=self.member)
        create_response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response_id = create_response.data["id"]

        response = self.client.delete(f"{self.responses_url}{response_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(PollResponse.objects.count(), 0)

    def test_member_cannot_delete_other_members_response(self):
        self.client.force_authenticate(user=self.member)
        create_response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response_id = create_response.data["id"]

        self.client.force_authenticate(user=self.other_member)
        response = self.client.delete(f"{self.responses_url}{response_id}/")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(PollResponse.objects.count(), 1)

    def test_admin_can_update_any_response(self):
        self.client.force_authenticate(user=self.member)
        create_response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response_id = create_response.data["id"]

        self.client.force_authenticate(user=self.admin)
        response = self.client.patch(
            f"{self.responses_url}{response_id}/",
            {"available": False},
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_admin_can_delete_any_response(self):
        self.client.force_authenticate(user=self.member)
        create_response = self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )
        response_id = create_response.data["id"]

        self.client.force_authenticate(user=self.admin)
        response = self.client.delete(f"{self.responses_url}{response_id}/")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_responses_scoped_to_poll(self):
        self.client.force_authenticate(user=self.member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )

        # create a second poll
        self.client.force_authenticate(user=self.admin)
        other_poll = self.client.post("/api/polls/", {"title": "July Dates"})
        other_responses_url = f"/api/polls/{other_poll.data['id']}/responses/"

        response = self.client.get(other_responses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

    def test_member_can_list_responses(self):
        self.client.force_authenticate(user=self.member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": True},
        )

        self.client.force_authenticate(user=self.other_member)
        self.client.post(
            self.responses_url,
            {"date_option": self.date_id_1, "available": False},
        )

        response = self.client.get(self.responses_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_missing_required_fields_returns_400(self):
        self.client.force_authenticate(user=self.member)
        response = self.client.post(
            self.responses_url,
            {"comment": "maybe"},
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthenticated_cannot_access_responses(self):
        self.client.force_authenticate(user=None)
        response = self.client.get(self.responses_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
