from django.urls import path

from . import views

LIST_ACTIONS = { "get": "list", "post": "create" }
DETAIL_ACTIONS = { "get": "retrieve", "put": "update", "patch": "partial_update", "delete": "destroy" }

urlpatterns = [
    path(
        "events/",
        views.EventViewSet.as_view(LIST_ACTIONS),
        name="event-list"
    ),
    path(
        "events/<uuid:pk>/",
        views.EventViewSet.as_view(DETAIL_ACTIONS),
        name="event-detail"
    ),
    path(
        "polls/",
        views.PollViewSet.as_view(LIST_ACTIONS),
        name="poll-list"
    ),
    path(
        "polls/<uuid:pk>/",
        views.PollViewSet.as_view(DETAIL_ACTIONS),
        name="poll-detail"
    ),
    path(
        "polls/<uuid:poll_id>/invitations/",
        views.PollInvitationListCreateView.as_view(),
        name="poll-invitations"
    ),
    path(
        "polls/<uuid:poll_id>/invitations/<uuid:pk>/",
        views.PollInvitationDetailView.as_view(),
        name="poll-invitation-detail"
    ),
    path(
        "polls/<uuid:poll_id>/date-options/",
        views.PollDateListCreateView.as_view(),
        name="poll-date-options"
    ),
    path(
        "polls/<uuid:poll_id>/date-options/<uuid:pk>/",
        views.PollDateDetailView.as_view(),
        name="poll-date-option-detail"
    ),
    path(
        "polls/<uuid:poll_id>/responses/",
        views.PollResponseListCreateView.as_view(),
        name="poll-responses"
    ),
    path(
        "polls/<uuid:poll_id>/responses/<uuid:pk>/",
        views.PollResponseDetailView.as_view(),
        name="poll-response-detail"
    )
]
