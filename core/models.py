import uuid

from django.contrib.auth.models import AbstractUser
from django.db import models


class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid7, editable=False)
