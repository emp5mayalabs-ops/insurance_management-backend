# agent_portal/views.py
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from agent_portal.serializers import (
    AgentLoginSerializer,
    AgentProfileSerializer,
)


# =========================================================
# AGENT LOGIN
# =========================================================

class AgentLoginView(APIView):
    """
    POST /api/agent/login/
    Body: { "username": "...", "password": "..." }
    """

    permission_classes = []

    def post(self, request):
        # Defensive: request.data must be a dict
        if not isinstance(request.data, dict):
            return Response(
                {
                    "success": False,
                    "message": "Invalid request body. Send JSON.",
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        serializer = AgentLoginSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_401_UNAUTHORIZED,
            )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)

        # Also add custom claims so the frontend can gate on "agent"
        refresh["role"] = "agent"
        refresh["agent_id"] = user.agent_profile.agent_id
        refresh["username"] = user.username

        return Response(
            {
                "success": True,
                "message": "Agent login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "agent": AgentProfileSerializer(
                    user.agent_profile
                ).data,
            },
            status=status.HTTP_200_OK,
        )


# =========================================================
# AGENT ME (profile of the logged-in agent)
# =========================================================

class AgentMeView(APIView):
    """
    GET /api/agent/me/
    Header: Authorization: Bearer <access_token>
    """

    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if not hasattr(user, "agent_profile"):
            return Response(
                {
                    "success": False,
                    "message": "This account is not an agent account.",
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        return Response(
            {
                "success": True,
                "agent": AgentProfileSerializer(
                    user.agent_profile
                ).data,
            },
            status=status.HTTP_200_OK,
        )