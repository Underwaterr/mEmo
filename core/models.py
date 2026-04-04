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
    display_name = models.CharField(max_length=120)

