# agent_portal/serializers.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from agent_portal.models import AgentProfile


# =========================================================
# AGENT LOGIN
# =========================================================

class AgentLoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, attrs):
        username = attrs.get("username")
        password = attrs.get("password")

        user = authenticate(
            request=self.context.get("request"),
            username=username,
            password=password,
        )

        if user is None:
            raise serializers.ValidationError(
                {"detail": "Invalid username or password."}
            )

        if not user.is_active:
            raise serializers.ValidationError(
                {"detail": "This account is inactive."}
            )

        # Must have an AgentProfile
        if not hasattr(user, "agent_profile"):
            raise serializers.ValidationError(
                {"detail": "This account is not an agent account."}
            )

        if not user.agent_profile.is_active:
            raise serializers.ValidationError(
                {"detail": "Your agent account has been deactivated."}
            )

        attrs["user"] = user
        return attrs


# =========================================================
# AGENT PROFILE (for the logged-in agent)
# =========================================================

class AgentProfileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="user.id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    is_user_active = serializers.BooleanField(
        source="user.is_active", read_only=True
    )

    class Meta:
        model = AgentProfile
        fields = [
            "id",
            "username",
            "email",
            "agent_id",
            "phone",
            "is_active",
            "is_user_active",
            "created_at",
        ]
        read_only_fields = fields