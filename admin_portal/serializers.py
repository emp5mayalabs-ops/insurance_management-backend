from django.contrib.auth.models import User
from rest_framework import serializers

from agent_portal.models import AgentProfile


# =========================================================
# CREATE AGENT
# =========================================================

class AgentCreateSerializer(serializers.Serializer):

    username = serializers.CharField(
        max_length=150
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    email = serializers.EmailField()

    agent_id = serializers.CharField(
        max_length=50
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True
    )

    def validate_username(self, value):

        if User.objects.filter(
            username=value
        ).exists():

            raise serializers.ValidationError(
                "Username already exists."
            )

        return value

    def validate_agent_id(self, value):

        if AgentProfile.objects.filter(
            agent_id=value
        ).exists():

            raise serializers.ValidationError(
                "Agent ID already exists."
            )

        return value

    def create(self, validated_data):

        username = validated_data["username"]

        password = validated_data["password"]

        email = validated_data["email"]

        agent_id = validated_data["agent_id"]

        phone = validated_data.get(
            "phone",
            ""
        )

        # Create Django User
        user = User.objects.create_user(
            username=username,
            password=password,
            email=email
        )

        # Create Agent Profile
        AgentProfile.objects.create(
            user=user,
            agent_id=agent_id,
            phone=phone
        )

        return user


# =========================================================
# VIEW AGENT
# =========================================================

class AgentSerializer(serializers.ModelSerializer):

    # IMPORTANT:
    # Do NOT use source="username" here.
    username = serializers.CharField(
        read_only=True
    )

    email = serializers.EmailField(
        read_only=True
    )

    agent_id = serializers.CharField(
        source="agent_profile.agent_id",
        read_only=True
    )

    phone = serializers.CharField(
        source="agent_profile.phone",
        read_only=True
    )

    is_active = serializers.BooleanField(
        source="agent_profile.is_active",
        read_only=True
    )

    created_at = serializers.DateTimeField(
        source="agent_profile.created_at",
        read_only=True
    )

    class Meta:

        model = User

        fields = [
            "id",
            "username",
            "email",
            "agent_id",
            "phone",
            "is_active",
            "created_at",
        ]

        read_only_fields = [
            "id",
            "username",
            "email",
            "agent_id",
            "phone",
            "is_active",
            "created_at",
        ]


# =========================================================
# UPDATE AGENT
# =========================================================

class AgentUpdateSerializer(serializers.Serializer):

    email = serializers.EmailField(
        required=False
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True
    )

    is_active = serializers.BooleanField(
        required=False
    )

    def update(
        self,
        user,
        validated_data
    ):

        # Update email
        if "email" in validated_data:

            user.email = validated_data["email"]

            user.save()


        # Get Agent Profile
        agent = user.agent_profile


        # Update phone
        if "phone" in validated_data:

            agent.phone = validated_data["phone"]


        # Update active status
        if "is_active" in validated_data:

            agent.is_active = validated_data["is_active"]

            # Keep Django User status synchronized
            user.is_active = validated_data["is_active"]

            user.save()


        agent.save()

        return user