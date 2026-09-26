# customer_portal/serializers.py
import re

from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from rest_framework import serializers

from customer_portal.models import CustomerProfile


# =========================================================
# CREATE CUSTOMER  (called by an agent)
# =========================================================

class CustomerCreateSerializer(serializers.Serializer):

    # -------- USER ACCOUNT --------
    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True, min_length=8)
    email = serializers.EmailField()

    # -------- BASIC --------
    customer_id = serializers.CharField(max_length=50)
    phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    date_of_birth = serializers.DateField(
        required=False, allow_null=True
    )
    gender = serializers.ChoiceField(
        choices=CustomerProfile._meta.get_field("gender").choices,
        required=False,
        allow_blank=True,
    )

    # -------- ID PROOF --------
    aadhaar_number = serializers.CharField(
        max_length=12, required=False, allow_blank=True
    )
    pan_number = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )

    # -------- ADDRESS --------
    address_line1 = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    address_line2 = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    city = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    state = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    pincode = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )

    # ---------------------------------------------------
    # VALIDATION
    # ---------------------------------------------------

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists.")
        return value

    def validate_customer_id(self, value):
        if CustomerProfile.objects.filter(customer_id=value).exists():
            raise serializers.ValidationError("Customer ID already exists.")
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
        # The agent is passed via context from the view
        agent_user = self.context.get("agent_user")

        password = validated_data.pop("password")

        # Create Django User
        user = User.objects.create_user(
            username=validated_data["username"],
            password=password,
            email=validated_data["email"],
        )

        # Create CustomerProfile
        CustomerProfile.objects.create(
            user=user,
            created_by_agent=agent_user,
            customer_id=validated_data["customer_id"],
            phone=validated_data.get("phone", ""),
            date_of_birth=validated_data.get("date_of_birth"),
            gender=validated_data.get("gender", ""),
            aadhaar_number=validated_data.get("aadhaar_number", ""),
            pan_number=validated_data.get("pan_number", ""),
            address_line1=validated_data.get("address_line1", ""),
            address_line2=validated_data.get("address_line2", ""),
            city=validated_data.get("city", ""),
            state=validated_data.get("state", ""),
            pincode=validated_data.get("pincode", ""),
        )

        return user


# =========================================================
# VIEW CUSTOMER
# =========================================================

class CustomerSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source="user.id", read_only=True)
    profile_id = serializers.IntegerField(source="id", read_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)

    created_by_agent_username = serializers.CharField(
        source="created_by_agent.username",
        read_only=True,
    )
    created_by_agent_id = serializers.CharField(
        source="created_by_agent.agent_profile.agent_id",
        read_only=True,
        allow_null=True,
    )

    class Meta:
        model = CustomerProfile
        fields = [
            "id",
            "profile_id",
            "username",
            "email",
            "customer_id",
            "phone",
            "date_of_birth",
            "gender",
            "aadhaar_number",
            "pan_number",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "pincode",
            "is_active",
            "created_by_agent_username",
            "created_by_agent_id",
            "created_at",
        ]
        read_only_fields = fields


# =========================================================
# CUSTOMER LOGIN
# =========================================================

class CustomerLoginSerializer(serializers.Serializer):

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

        if not hasattr(user, "customer_profile"):
            raise serializers.ValidationError(
                {"detail": "This account is not a customer account."}
            )

        if not user.customer_profile.is_active:
            raise serializers.ValidationError(
                {"detail": "Your customer account has been deactivated."}
            )

        attrs["user"] = user
        return attrs


# =========================================================
# UPDATE CUSTOMER
# =========================================================

class CustomerUpdateSerializer(serializers.Serializer):

    email = serializers.EmailField(required=False)
    phone = serializers.CharField(
        max_length=20, required=False, allow_blank=True
    )
    date_of_birth = serializers.DateField(
        required=False, allow_null=True
    )
    gender = serializers.ChoiceField(
        choices=CustomerProfile._meta.get_field("gender").choices,
        required=False,
        allow_blank=True,
    )
    aadhaar_number = serializers.CharField(
        max_length=12, required=False, allow_blank=True
    )
    pan_number = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )
    address_line1 = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    address_line2 = serializers.CharField(
        max_length=255, required=False, allow_blank=True
    )
    city = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    state = serializers.CharField(
        max_length=100, required=False, allow_blank=True
    )
    pincode = serializers.CharField(
        max_length=10, required=False, allow_blank=True
    )
    is_active = serializers.BooleanField(required=False)

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

    def update(self, user, validated_data):
        profile = user.customer_profile

        if "email" in validated_data:
            user.email = validated_data["email"]

        if "is_active" in validated_data:
            user.is_active = validated_data["is_active"]
            profile.is_active = validated_data["is_active"]

        for field in [
            "phone",
            "date_of_birth",
            "gender",
            "aadhaar_number",
            "pan_number",
            "address_line1",
            "address_line2",
            "city",
            "state",
            "pincode",
        ]:
            if field in validated_data:
                setattr(profile, field, validated_data[field])

        user.save()
        profile.save()
        return user