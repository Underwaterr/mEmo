from rest_framework import serializers

from .models import Event, Poll, PollInvitation, PollDate, PollResponse


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


class PollInvitationSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = PollInvitation
        fields = BaseSerializer.Meta.fields + [
            "poll",
            "user",
        ]
        read_only_fields = BaseSerializer.Meta.read_only_fields + [
            "poll"
        ]


class PollDateSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = PollDate
        fields = BaseSerializer.Meta.fields + [
            "poll",
            "date",
            "start_time",
        ]
        read_only_fields = BaseSerializer.Meta.read_only_fields + [
             "poll"
        ]


class PollResponseSerializer(BaseSerializer):
    class Meta(BaseSerializer.Meta):
        model = PollResponse
        fields = BaseSerializer.Meta.fields + [
            "date_option",
            "user",
            "available",
            "comment",
        ]
        read_only_fields = BaseSerializer.Meta.read_only_fields + [
            "user"
        ]
