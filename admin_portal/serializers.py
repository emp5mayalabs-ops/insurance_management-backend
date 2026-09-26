# admin_portal/serializers.py
import re

from django.contrib.auth.models import User
from rest_framework import serializers

from agent_portal.models import AgentProfile


# =========================================================
# CREATE AGENT
# =========================================================

class AgentCreateSerializer(serializers.Serializer):

    # -------- USER ACCOUNT --------
    username = serializers.CharField(
        max_length=150
    )

    password = serializers.CharField(
        write_only=True,
        min_length=8
    )

    email = serializers.EmailField()

    # -------- BASIC --------
    agent_id = serializers.CharField(
        max_length=50
    )

    phone = serializers.CharField(
        max_length=20,
        required=False,
        allow_blank=True
    )

    # -------- ID PROOF --------
    aadhaar_number = serializers.CharField(
        max_length=12,
        required=False,
        allow_blank=True
    )

    pan_number = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True
    )

    # -------- INSURANCE COMPANY --------
    insurance_company = serializers.ChoiceField(
        choices=AgentProfile.INSURANCE_COMPANY_CHOICES,
        required=False,
        allow_blank=True
    )

    # -------- ADDRESS --------
    address_line1 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    address_line2 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    city = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    state = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    pincode = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True
    )

    # ---------------------------------------------------
    # FIELD-LEVEL VALIDATION
    # ---------------------------------------------------

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

    def validate_aadhaar_number(self, value):

        if not value:
            return value

        if not re.fullmatch(r"\d{12}", value):

            raise serializers.ValidationError(
                "Aadhaar must be exactly 12 digits."
            )

        return value

    def validate_pan_number(self, value):

        if not value:
            return value

        value = value.upper()

        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):

            raise serializers.ValidationError(
                "PAN must be in format ABCDE1234F."
            )

        return value

    def validate_pincode(self, value):

        if not value:
            return value

        if not re.fullmatch(r"\d{6}", value):

            raise serializers.ValidationError(
                "Pincode must be exactly 6 digits."
            )

        return value

    # ---------------------------------------------------
    # CREATE
    # ---------------------------------------------------

    def create(self, validated_data):

        username = validated_data["username"]

        password = validated_data["password"]

        email = validated_data["email"]

        agent_id = validated_data["agent_id"]

        phone = validated_data.get("phone", "")

        aadhaar_number = validated_data.get(
            "aadhaar_number", ""
        )

        pan_number = validated_data.get(
            "pan_number", ""
        )

        insurance_company = validated_data.get(
            "insurance_company", ""
        )

        address_line1 = validated_data.get(
            "address_line1", ""
        )

        address_line2 = validated_data.get(
            "address_line2", ""
        )

        city = validated_data.get("city", "")

        state = validated_data.get("state", "")

        pincode = validated_data.get("pincode", "")

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
            phone=phone,
            aadhaar_number=aadhaar_number,
            pan_number=pan_number,
            insurance_company=insurance_company,
            address_line1=address_line1,
            address_line2=address_line2,
            city=city,
            state=state,
            pincode=pincode
        )

        return user


# =========================================================
# VIEW AGENT
# =========================================================

class AgentSerializer(serializers.ModelSerializer):

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

    aadhaar_number = serializers.CharField(
        source="agent_profile.aadhaar_number",
        read_only=True
    )

    pan_number = serializers.CharField(
        source="agent_profile.pan_number",
        read_only=True
    )

    insurance_company = serializers.CharField(
        source="agent_profile.insurance_company",
        read_only=True
    )

    insurance_company_display = serializers.CharField(
        source="agent_profile.get_insurance_company_display",
        read_only=True
    )

    address_line1 = serializers.CharField(
        source="agent_profile.address_line1",
        read_only=True
    )

    address_line2 = serializers.CharField(
        source="agent_profile.address_line2",
        read_only=True
    )

    city = serializers.CharField(
        source="agent_profile.city",
        read_only=True
    )

    state = serializers.CharField(
        source="agent_profile.state",
        read_only=True
    )

    pincode = serializers.CharField(
        source="agent_profile.pincode",
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
            "aadhaar_number",
            "pan_number",
            "insurance_company",
            "insurance_company_display",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "pincode",
            "is_active",
            "created_at",
        ]

        read_only_fields = fields


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

    aadhaar_number = serializers.CharField(
        max_length=12,
        required=False,
        allow_blank=True
    )

    pan_number = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True
    )

    insurance_company = serializers.ChoiceField(
        choices=AgentProfile.INSURANCE_COMPANY_CHOICES,
        required=False,
        allow_blank=True
    )

    address_line1 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    address_line2 = serializers.CharField(
        max_length=255,
        required=False,
        allow_blank=True
    )

    city = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    state = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True
    )

    pincode = serializers.CharField(
        max_length=10,
        required=False,
        allow_blank=True
    )

    is_active = serializers.BooleanField(
        required=False
    )

    # ---------------------------------------------------
    # FIELD VALIDATION
    # ---------------------------------------------------

    def validate_aadhaar_number(self, value):

        if value and not re.fullmatch(r"\d{12}", value):

            raise serializers.ValidationError(
                "Aadhaar must be exactly 12 digits."
            )

        return value

    def validate_pan_number(self, value):

        if not value:
            return value

        value = value.upper()

        if not re.fullmatch(r"[A-Z]{5}[0-9]{4}[A-Z]", value):

            raise serializers.ValidationError(
                "PAN must be in format ABCDE1234F."
            )

        return value

    def validate_pincode(self, value):

        if value and not re.fullmatch(r"\d{6}", value):

            raise serializers.ValidationError(
                "Pincode must be exactly 6 digits."
            )

        return value

    # ---------------------------------------------------
    # UPDATE
    # ---------------------------------------------------

    def update(self, user, validated_data):

        agent = user.agent_profile

        # -------- USER FIELDS --------
        if "email" in validated_data:

            user.email = validated_data["email"]

        if "is_active" in validated_data:

            user.is_active = validated_data["is_active"]

            agent.is_active = validated_data["is_active"]

        # -------- PROFILE FIELDS --------
        profile_fields = [
            "phone",
            "aadhaar_number",
            "pan_number",
            "insurance_company",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "pincode",
        ]

        for field in profile_fields:

            if field in validated_data:

                setattr(
                    agent,
                    field,
                    validated_data[field]
                )

        user.save()
        agent.save()

        return user