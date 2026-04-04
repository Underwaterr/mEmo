from rest_framework import serializers

from .models import Event, Poll


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class EventSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Event
        fields = BaseSerializer.Meta.fields + [
            "title",
            "type",
            "date",
            "start_time",
            "location",
            "status",
            "info",
        ]


class PollSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = Poll
        fields = BaseSerializer.Meta.fields + [
            "title",
            "deadline",
            "closed"
        ]
