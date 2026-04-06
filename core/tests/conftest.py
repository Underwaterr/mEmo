import pytest
from rest_framework.test import APIClient

from core.models import User


@pytest.fixture
def client():
    return APIClient()


@pytest.fixture
def admin(db):
    return User.objects.create_user(
        username="garfield",
        password="password",
        display_name="Garf",
        is_staff=True
    )


@pytest.fixture
def odie(db):
    return User.objects.create_user(
        username="odie",
        password="password2",
        display_name="Odie",
        is_staff=False
    )


@pytest.fixture
def jon(db):
    return User.objects.create_user(
        username="arbuckle77",
        password="cool-guy-alert",
        display_name="Jon",
        is_staff=False
    )


@pytest.fixture
def arlene(db):
    return User.objects.create_user(
        username="arlene",
        password="password2",
        display_name="Arlene",
        is_staff=False,
    )


@pytest.fixture
def nermal(db):
    return User.objects.create_user(
        username="nermal",
        password="password3",
        display_name="Cutie",
        is_staff=False,
    )


@pytest.fixture
def client_admin(admin):
    client = APIClient()
    client.force_authenticate(user=admin)
    return client


@pytest.fixture
def client_odie(odie):
    client = APIClient()
    client.force_authenticate(user=odie)
    return client


@pytest.fixture
def client_jon(jon):
    client = APIClient()
    client.force_authenticate(user=jon)
    return client


@pytest.fixture
def event_data():
    return {
        "title": "Shea Stadium",
        "type": "gig",
        "date": "2026-05-15",
        "status": "pending"
    }


@pytest.fixture
def poll_dates_url(client_admin):
    response = client_admin.post("/api/polls/", {"title": "June Dates"})
    poll_id = response.data["id"]
    return f"/api/polls/{poll_id}/date-options/"


@pytest.fixture
def invitation_url(client_admin):
    response = client_admin.post("/api/polls/", {"title": "June Dates"})
    poll_id = response.data["id"]
    return f"/api/polls/{poll_id}/invitations/"


@pytest.fixture
def poll(client_admin):
    response = client_admin.post("/api/polls/", {"title": "June Dates"})
    poll_id = response.data["id"]
    dates_url = f"/api/polls/{poll_id}/date-options/"
    first_date_response = client_admin.post(dates_url, {"date": "2026-06-14"})
    second_date_response = client_admin.post(dates_url, {"date": "2026-06-21"})
    return { 
        "url": f"/api/polls/{poll_id}/responses/",
        "dates": [ first_date_response.data["id"], second_date_response.data["id"] ]
    }
