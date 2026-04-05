import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    # instead of `BigAutoField`, use UUIDv7 for IDs
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)

    # automatically track when a new row is created and when a row is updated
    created_at = models.DateTimeField(auto_now_add=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # this is not an actual database table
        # it exists only to be inherited from
        abstract = True


class User(AbstractUser):
    # override the AbstractUser's `id` field with our UUIDv7 IDs
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    display_name = models.CharField(max_length=128)


class EventType(models.TextChoices):
    GIG = "gig"
    REHEARSAL = "rehearsal"
    MEETING = "meeting"
    OTHER = "other"


class EventStatus(models.TextChoices):
    CONFIRMED = "confirmed"
    PENDING = "pending"
    CANCELED = "canceled"


class Event(BaseModel):
    title = models.CharField(max_length=256)
    type = models.CharField(max_length=32, choices=EventType.choices)
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)
    location = models.CharField(max_length=256, blank=True, default="")
    status = models.CharField(max_length=32, choices=EventStatus.choices, default=EventStatus.PENDING)
    info = models.TextField(blank=True, default="")

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.title} ({self.date})"


class Poll(BaseModel):
    title = models.CharField(max_length=256)
    deadline = models.DateTimeField(null=True, blank=True)
    closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title 


class PollInvitation(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="invitations")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poll_invitations")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["poll", "user"],
                name="unique_invitation_per_user_per_poll",
            )
        ]

    def __str__(self):
        return f"{self.user} invited to {self.poll}"


class PollDate(BaseModel):
    poll = models.ForeignKey(Poll, on_delete=models.CASCADE, related_name="date_options")
    date = models.DateField()
    start_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ["date", "start_time"]

    def __str__(self):
        return f"{self.poll.title} - {self.date}"


class PollResponse(BaseModel):
    date_option = models.ForeignKey(PollDate, on_delete=models.CASCADE, related_name="responses")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="poll_responses")
    available = models.BooleanField()
    comment = models.CharField(max_length=256, blank=True, default="")

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["date_option", "user"],
                name="unique_response_per_user_per_option",
            )
        ]

    def __str__(self):
        status = "available" if self.available else "unavailable"
        return f"{self.user} - {self.date_option} - {status}"
