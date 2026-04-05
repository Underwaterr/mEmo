from rest_framework import viewsets, permissions, generics, serializers
from django.shortcuts import get_object_or_404

from .models import (
    Event,
    Poll, 
    PollInvitation, 
    PollDate, 
    PollResponse
)
from .serializers import (
    EventSerializer, 
    PollSerializer,
    PollInvitationSerializer,
    PollDateSerializer,
    PollResponseSerializer
)

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user.is_staff

class IsOwnerOrAdmin(permissions.BasePermission):
    # has_object_permission is called *after* the object is retrieved
    # so we can check whether the user owns it
    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        if request.user.is_staff:
            return True
        return obj.user == request.user


# Create, Read, Update, Delete Events
class EventViewSet(viewsets.ModelViewSet):
    queryset = Event.objects.all()
    serializer_class = EventSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


# Create, Read, Update, Delete Polls
class PollViewSet(viewsets.ModelViewSet):
    queryset = Poll.objects.all()
    serializer_class = PollSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]


# Create and List Poll Invitations
class PollInvitationListCreateView(generics.ListCreateAPIView):
    serializer_class = PollInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # we'll always get poll invitations related to a specific poll
        return PollInvitation.objects.filter(poll_id=self.kwargs["poll_id"])

    def perform_create(self, serializer):
        # when creating a poll invitation, include a reference to the poll
        poll = get_object_or_404(Poll, pk=self.kwargs["poll_id"])

        # when one field in a unique constraint comes from the URL rather than the request body, 
        # validation has to happen in the view where both values are available
        if PollInvitation.objects.filter(poll=poll, user=serializer.validated_data["user"]).exists():
            raise serializers.ValidationError({"user": "This user has already been invited to this poll."})

        serializer.save(poll=poll)


# Get, Update and Delete Poll Invitation
class PollInvitationDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PollInvitationSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # we'll always get poll invitations related to a specific poll
        return PollInvitation.objects.filter(poll_id=self.kwargs["poll_id"])


# Create and List Poll Dates
class PollDateListCreateView(generics.ListCreateAPIView):
    serializer_class = PollDateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # we'll always get poll dates related to a specific poll
        return PollDate.objects.filter(poll_id=self.kwargs["poll_id"])

    def perform_create(self, serializer):
        # when creating a poll date, include a reference to the poll
        poll = get_object_or_404(Poll, pk=self.kwargs["poll_id"])
        serializer.save(poll=poll)


# Get, Update and Delete Poll Date
class PollDateDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PollDateSerializer
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]

    def get_queryset(self):
        # we'll always get poll dates related to a specific poll
        return PollDate.objects.filter(poll_id=self.kwargs["poll_id"])


# Create and List Poll Responses
class PollResponseListCreateView(generics.ListCreateAPIView):
    serializer_class = PollResponseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        # get the poll by joining on `date_option` and `poll_id`
        return PollResponse.objects.filter(date_option__poll_id=self.kwargs["poll_id"])

    def perform_create(self, serializer):
        # similar to with PollInvitation,
        # validation has to happen in the view where both values are available
        date_option = serializer.validated_data["date_option"]
        if PollResponse.objects.filter(date_option=date_option, user=self.request.user).exists():
            raise serializers.ValidationError({"date_option": "You have already responded to this date option."})
        # automatically get who the user is by who is making the request
        serializer.save(user=self.request.user)


# Get, Update and Delete Poll Response
class PollResponseDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = PollResponseSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrAdmin]

    def get_queryset(self):
        # get the poll by joining on `date_option` and `poll_id`
        return PollResponse.objects.filter(date_option__poll_id=self.kwargs["poll_id"])
