from rest_framework import serializers
from django.contrib.auth import authenticate

from .models import User, Event, Poll, PollInvitation, PollDate, PollResponse


class BaseSerializer(serializers.ModelSerializer):
    class Meta:
        fields = ["id", "created_at", "updated_at"]
        read_only_fields = ["id", "created_at", "updated_at"]


class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        user = authenticate(
            username=attrs["username"],
            password=attrs["password"],
        )
        if user is None:
            raise serializers.ValidationError("Invalid username or password.")
        if not user.is_active:
            raise serializers.ValidationError("This account is inactive.")
        attrs["user"] = user
        return attrs


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "display_name",
            "is_staff",
            "last_login",
            "date_joined"
        ]
        read_only_fields = [
            "id",
            "username",
            "is_staff",
            "date_joined"
        ]


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
    user_detail = UserSerializer(source="user", read_only=True)

    class Meta(BaseSerializer.Meta):
        model = PollInvitation
        fields = BaseSerializer.Meta.fields + [
            "poll",
            "user",
            "user_detail"
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
    user = UserSerializer(read_only=True)
    date_option_detail = PollDateSerializer(source="date_option", read_only=True)

    class Meta(BaseSerializer.Meta):
        model = PollResponse
        fields = BaseSerializer.Meta.fields + [
            "date_option",
            "date_option_detail",
            "user",
            "available",
            "comment",
        ]
        read_only_fields = BaseSerializer.Meta.read_only_fields + [
            "user"
        ]
