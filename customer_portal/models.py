# customer_portal/models.py
from django.db import models
from django.conf import settings


class CustomerProfile(models.Model):

    # ---------------------------------------------------
    # LINK TO DJANGO USER + CREATING AGENT
    # ---------------------------------------------------
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="customer_profile",
    )

    created_by_agent = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customers_created",
        help_text="Agent who created this customer"
    )

    # ---------------------------------------------------
    # BASIC
    # ---------------------------------------------------
    customer_id = models.CharField(
        max_length=50,
        unique=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True,
        default=""
    )

    date_of_birth = models.DateField(
        null=True,
        blank=True
    )

    gender = models.CharField(
        max_length=10,
        choices=[
            ("MALE", "Male"),
            ("FEMALE", "Female"),
            ("OTHER", "Other"),
        ],
        blank=True,
        default=""
    )

    # ---------------------------------------------------
    # ID PROOF
    # ---------------------------------------------------
    aadhaar_number = models.CharField(
        max_length=12,
        blank=True,
        default=""
    )

    pan_number = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )

    # ---------------------------------------------------
    # ADDRESS
    # ---------------------------------------------------
    address_line1 = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    address_line2 = models.CharField(
        max_length=255,
        blank=True,
        default=""
    )

    city = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    state = models.CharField(
        max_length=100,
        blank=True,
        default=""
    )

    pincode = models.CharField(
        max_length=10,
        blank=True,
        default=""
    )

    # ---------------------------------------------------
    # STATUS / META
    # ---------------------------------------------------
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.customer_id} ({self.user.username})"