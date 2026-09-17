from django.db import models
from django.contrib.auth.models import User


class AgentProfile(models.Model):

    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="agent_profile"
    )

    agent_id = models.CharField(
        max_length=50,
        unique=True
    )

    phone = models.CharField(
        max_length=20,
        blank=True
    )

    is_active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.agent_id} - {self.user.username}"