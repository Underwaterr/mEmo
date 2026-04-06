import pytest
from rest_framework import status

from core.models import Poll, PollInvitation, PollDate, PollResponse

@pytest.mark.django_db
class TestPollDates:

    def test_admin_can_create_date(self, client_admin, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        response = client_admin.post(poll_dates_url, date_data)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["date"] == "2026-06-14"
        assert response.data["start_time"] == "20:00:00"
        assert PollDate.objects.count() == 1

    def test_date_belongs_to_poll(self, client_admin):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        create_response = client_admin.post("/api/polls/", {"title": "June Dates"})
        poll_id = create_response.data["id"]
        poll_dates_url = f"/api/polls/{poll_id}/date-options/"
        response = client_admin.post(poll_dates_url, date_data)
        assert str(response.data["poll"]) == poll_id

    def test_date_without_start_time(self, client_admin, poll_dates_url):
        response = client_admin.post(poll_dates_url, {"date": "2026-06-14"})
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["start_time"] is None

    def test_admin_can_create_multiple_dates(self, client_admin, poll_dates_url):
        client_admin.post(poll_dates_url, {"date": "2026-06-14"})
        client_admin.post(poll_dates_url, {"date": "2026-06-21"})
        client_admin.post(poll_dates_url, {"date": "2026-06-28"})
        assert PollDate.objects.count() == 3

    def test_odie_cannot_create_date(self, client_odie, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        response = client_odie.post(poll_dates_url, date_data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_odie_can_list_dates(self, client_admin, client_odie, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        client_admin.post(poll_dates_url, date_data)

        response = client_odie.get(poll_dates_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_dates_scoped_to_poll(self, client_admin, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        client_admin.post(poll_dates_url, date_data)

        response = client_admin.post("/api/polls/", {"title": "July Dates"})
        other_dates_url = f"/api/polls/{response.data['id']}/date-options/"

        response = client_admin.get(other_dates_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_dates_ordered_by_date_and_time(self, client_admin, poll_dates_url):
        client_admin.post(poll_dates_url, {"date": "2026-06-28"})
        client_admin.post(poll_dates_url, {"date": "2026-06-14", "start_time": "21:00:00"})
        client_admin.post(poll_dates_url, {"date": "2026-06-14", "start_time": "18:00:00"})

        response = client_admin.get(poll_dates_url)
        dates = [(d["date"], d["start_time"]) for d in response.data]
        assert dates == [("2026-06-14","18:00:00"), ("2026-06-14","21:00:00"), ("2026-06-28",None)]

    def test_admin_can_update_date(self, client_admin, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        create_response = client_admin.post(poll_dates_url, date_data)
        date_id = create_response.data["id"]
        response = client_admin.patch(f"{poll_dates_url}{date_id}/", {"start_time": "21:00:00"})
        assert response.status_code == status.HTTP_200_OK
        assert response.data["start_time"] == "21:00:00"

    def test_odie_cannot_update_date(self, client_admin, client_odie, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        create_response = client_admin.post(poll_dates_url, date_data)
        date_id = create_response.data["id"]
        response = client_odie.patch(f"{poll_dates_url}{date_id}/", {"start_time": "21:00:00"})
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_date(self, client_admin, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        create_response = client_admin.post(poll_dates_url, date_data)
        date_id = create_response.data["id"]
        response = client_admin.delete(f"{poll_dates_url}{date_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert PollDate.objects.count() == 0

    def test_odie_cannot_delete_date(self, client_admin, client_odie, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        create_response = client_admin.post(poll_dates_url, date_data)
        date_id = create_response.data["id"]
        response = client_odie.delete(f"{poll_dates_url}{date_id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert PollDate.objects.count() == 1

    def test_nonexistent_poll_returns_404(self, client_admin, poll_dates_url):
        date_data = { "date": "2026-06-14", "start_time": "20:00:00" }
        fake_poll_id = "00000000-0000-0000-0000-000000000000"
        response = client_admin.post(
            f"/api/polls/{fake_poll_id}/date-options/",
            date_data,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_missing_date_field_returns_400(self, client_admin, poll_dates_url):
        response = client_admin.post(
            poll_dates_url,
            {"start_time": "20:00:00"},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_cannot_access_dates(self, client, poll_dates_url):
        response = client.get(poll_dates_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPollResponse:

    def test_odie_can_respond(self, client_odie, poll):
        response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["available"] == True
        assert PollResponse.objects.count() == 1

    def test_response_user_set_automatically(self, client_odie, odie, poll):
        response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        assert str(response.data["user"]) == str(odie.id)

    def test_odie_can_respond_to_multiple_dates(self, client_odie, poll):
        response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response = client_odie.post(poll["url"], { "date_option": poll["dates"][1], "available": False })
        assert PollResponse.objects.count() == 2

    def test_multiple_members_can_respond_to_same_date(self, client_jon, client_odie, poll):
        client_jon.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        assert PollResponse.objects.count() == 2

    def test_duplicate_response_rejected(self, client_odie, poll):
        client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": False })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PollResponse.objects.count() == 1

    def test_response_with_comment(self, client_odie, poll):
        poll_response = { "date_option": poll["dates"][0], "available": False, "comment": "Dentist" }
        response = client_odie.post(poll["url"], poll_response)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["comment"] == "Dentist"

    def test_odie_can_update_own_response(self, client_odie, poll):
        poll_response = { "date_option": poll["dates"][0], "available": False, "comment": "Dentist" }
        create_response = client_odie.post(poll["url"], poll_response)
        response_id = create_response.data["id"]
        response = client_odie.patch(f"{poll["url"]}{response_id}/", { "available": False })
        assert response.status_code == status.HTTP_200_OK
        assert response.data["available"] == False

    def test_odie_cannot_update_other_members_response(self, client_odie, client_jon, poll):
        create_response = client_jon.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response_id = create_response.data["id"]
        response = client_odie.patch(f"{poll["url"]}{response_id}/",{ "available": False })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_odie_can_delete_own_response(self, client_odie, poll):
        create_response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response_id = create_response.data["id"]
        response = client_odie.delete(f"{poll["url"]}{response_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert PollResponse.objects.count() == 0

    def test_odie_cannot_delete_other_members_response(self, client_odie, client_jon, poll):
        create_response = client_jon.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response_id = create_response.data["id"]
        response = client_odie.delete(f"{poll["url"]}{response_id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert PollResponse.objects.count() == 1

    def test_admin_can_update_any_response(self, client_admin, client_odie, poll):
        create_response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response_id = create_response.data["id"]
        response = client_admin.patch(f"{poll["url"]}{response_id}/", { "available": False })
        assert response.status_code == status.HTTP_200_OK

    def test_admin_can_delete_any_response(self, client_odie, client_admin, poll):
        create_response = client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        response_id = create_response.data["id"]
        response = client_admin.delete(f"{poll["url"]}{response_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT

    def test_responses_scoped_to_poll(self, client_odie, client_admin, poll):
        client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": False })
        other_poll = client_admin.post("/api/polls/", {"title": "July Dates"})
        other_responses_url = f"/api/polls/{other_poll.data['id']}/responses/"
        response = client_admin.get(other_responses_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_odie_can_list_responses(self, client_jon, client_odie, poll):
        client_jon.post(poll["url"], { "date_option": poll["dates"][0], "available": True })
        client_odie.post(poll["url"], { "date_option": poll["dates"][0], "available": False })
        response = client_odie.get(poll["url"])
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2

    def test_missing_required_fields_returns_400(self, client_odie, poll):
        response = client_odie.post(poll["url"], { "comment": "maybe" })
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_unauthenticated_cannot_access_responses(self, client, poll):
        response = client.get(poll["url"])
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPollInvitations:

    def test_admin_can_invite_user(self, client_admin, invitation_url, arlene):
        response = client_admin.post(invitation_url, { "user": arlene.id })
        assert response.status_code == status.HTTP_201_CREATED
        assert PollInvitation.objects.count() == 1

    def test_admin_can_invite_multiple_users(self, client_admin, invitation_url, arlene, nermal):
        client_admin.post(invitation_url, { "user": arlene.id })
        client_admin.post(invitation_url, { "user": nermal.id })
        assert PollInvitation.objects.count() == 2

    def test_duplicate_invitation_rejected(self, client_admin, invitation_url, arlene):
        client_admin.post(invitation_url, { "user": arlene.id })
        response = client_admin.post(invitation_url, { "user": arlene.id })
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert PollInvitation.objects.count() == 1

    def test_odie_cannot_invite(self, client_odie, invitation_url, nermal):
        response = client_odie.post(invitation_url, { "user": nermal.id })
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_odie_can_list_invitations(self, client_admin, client_odie, invitation_url, arlene):
        client_admin.post(invitation_url, { "user": arlene.id })
        response = client_admin.get(invitation_url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_admin_can_delete_invitation(self, client_admin, invitation_url, arlene):
        create_response = client_admin.post(invitation_url, { "user": arlene.id })
        invitation_id = create_response.data["id"]
        response = client_admin.delete(f"{invitation_url}{invitation_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert PollInvitation.objects.count() == 0

    def test_odie_cannot_delete_invitation(self, client_admin, client_odie, invitation_url, arlene):
        create_response = client_admin.post(invitation_url, { "user": arlene.id })
        invitation_id = create_response.data["id"]
        response = client_odie.delete(f"{invitation_url}{invitation_id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert PollInvitation.objects.count() == 1

    def test_invitation_scoped_to_poll(self, client_admin, invitation_url, arlene):
        client_admin.post(invitation_url, { "user": arlene.id })
        response = client_admin.post("/api/polls/", {"title": "August Dates"})
        other_poll_id = response.data["id"]
        response = client_admin.get(f"/api/polls/{other_poll_id}/invitations/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0

    def test_invitation_to_nonexistent_poll_returns_404(self, client_admin, arlene):
        fake_poll_id = "00000000-0000-0000-0000-000000000000"
        response = client_admin.post(f"/api/polls/{fake_poll_id}/invitations/", { "user": arlene.id })
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_unauthenticated_cannot_access_invitations(self, client, invitation_url):
        response = client.get(invitation_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestPolls():

    def test_admin_can_create_poll(self, client_admin):
        poll = { "title": "Shea Stadium" }
        response = client_admin.post("/api/polls/", poll)
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data["title"] == "Shea Stadium"
        assert Poll.objects.count() == 1

    def test_odie_cannot_create_poll(self, client_odie):
        poll = { "title": "Shea Stadium" }
        response = client_odie.post("/api/polls/", poll)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Poll.objects.count() == 0

    def test_unauthenticated_cannot_access_polls(self, client):
        response = client.get("/api/polls/")
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_odie_can_list_polls(self, client_admin, client_odie):
        poll = { "title": "Shea Stadium" }
        client_admin.post("/api/polls/", poll)
        response = client_odie.get("/api/polls/")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1

    def test_odie_can_retrieve_poll(self, client_admin, client_odie):
        poll = { "title": "Shea Stadium" }
        create_response = client_admin.post("/api/polls/", poll)
        poll_id = create_response.data["id"]
        response = client_odie.get(f"/api/polls/{poll_id}/")
        assert response.status_code == status.HTTP_200_OK
        assert response.data["title"] == "Shea Stadium"

    def test_admin_can_update_poll(self, client_admin):
        poll = { "title": "Shea Stadium" }
        create_response = client_admin.post("/api/polls/", poll)
        poll_id = create_response.data["id"]
        response = client_admin.patch(
            f"/api/polls/{poll_id}/",
            {"closed": True},
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["closed"] == True

    def test_odie_cannot_update_poll(self, client_admin, client_odie):
        poll = { "title": "Shea Stadium" }
        create_response = client_admin.post("/api/polls/", poll)
        poll_id = create_response.data["id"]
        response = client_odie.patch(
            f"/api/polls/{poll_id}/",
            {"closed": True},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_can_delete_poll(self, client_admin):
        poll = { "title": "Shea Stadium" }
        create_response = client_admin.post("/api/polls/", poll)
        poll_id = create_response.data["id"]
        response = client_admin.delete(f"/api/polls/{poll_id}/")
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Poll.objects.count() == 0

    def test_odie_cannot_delete_poll(self, client_admin, client_odie):
        poll = { "title": "Shea Stadium" }
        create_response = client_admin.post("/api/polls/", poll)
        poll_id = create_response.data["id"]
        response = client_odie.delete(f"/api/polls/{poll_id}/")
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert Poll.objects.count() == 1

    def test_create_poll_missing_required_field(self, client_admin):
        response = client_admin.post("/api/polls/", {"closed": True})
        assert response.status_code == status.HTTP_400_BAD_REQUEST
