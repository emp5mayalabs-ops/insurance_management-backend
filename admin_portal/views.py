# admin_portal/views.py
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
    AgentCreateSerializer,
    AgentSerializer,
    AgentUpdateSerializer
)


# =========================================================
# ADMIN LOGIN
# =========================================================

class AdminLoginView(APIView):

    permission_classes = []

    def post(self, request):

        # Defensive check: request.data must be a dict (JSON object).
        if not isinstance(request.data, dict):

            return Response(
                {
                    "success": False,
                    "message":
                        "Invalid request body. "
                        "Send JSON with Content-Type: application/json."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        username = request.data.get("username")
        password = request.data.get("password")

        if not username or not password:

            return Response(
                {
                    "success": False,
                    "message": "Username and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = authenticate(
            username=username,
            password=password
        )

        if user is None:

            return Response(
                {
                    "success": False,
                    "message": "Invalid username or password."
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        if not user.is_superuser:

            return Response(
                {
                    "success": False,
                    "message": "Admin access required."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if not user.is_active:

            return Response(
                {
                    "success": False,
                    "message": "Admin account is inactive."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        refresh = RefreshToken.for_user(user)

        return Response(
            {
                "success": True,
                "message": "Admin login successful.",

                "access": str(
                    refresh.access_token
                ),

                "refresh": str(refresh),

                "admin": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "is_superuser": user.is_superuser,
                }
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# CREATE AGENT
# =========================================================

class CreateAgentView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser
    ]

    def post(self, request):

        serializer = AgentCreateSerializer(
            data=request.data
        )

        if serializer.is_valid():

            user = serializer.save()
            profile = user.agent_profile

            return Response(
                {
                    "success": True,
                    "message": "Agent created successfully.",

                    "agent": {
                        "id": user.id,
                        "username": user.username,
                        "email": user.email,

                        # -------- BASIC --------
                        "agent_id": profile.agent_id,
                        "phone": profile.phone,

                        # -------- ID PROOF --------
                        "aadhaar_number":
                            profile.aadhaar_number,
                        "pan_number":
                            profile.pan_number,

                        # -------- INSURANCE --------
                        "insurance_company":
                            profile.insurance_company,
                        "insurance_company_display":
                            profile.get_insurance_company_display(),

                        # -------- ADDRESS --------
                        "address_line1":
                            profile.address_line1,
                        "address_line2":
                            profile.address_line2,
                        "city": profile.city,
                        "state": profile.state,
                        "pincode": profile.pincode,

                        # -------- STATUS --------
                        "is_active": profile.is_active,
                        "created_at": profile.created_at,
                    }
                },
                status=status.HTTP_201_CREATED
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# GET ALL AGENTS
# =========================================================

class AgentListView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser
    ]

    def get(self, request):

        agents = User.objects.filter(
            agent_profile__isnull=False
        ).select_related(
            "agent_profile"
        ).order_by("-id")

        serializer = AgentSerializer(
            agents,
            many=True
        )

        return Response(
            {
                "success": True,
                "count": agents.count(),
                "agents": serializer.data
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# GET SINGLE AGENT
# =========================================================

class AgentDetailView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser
    ]

    def get(self, request, agent_id):

        try:

            user = User.objects.select_related(
                "agent_profile"
            ).get(
                id=agent_id,
                agent_profile__isnull=False
            )

        except User.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Agent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentSerializer(user)

        return Response(
            {
                "success": True,
                "agent": serializer.data
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# UPDATE AGENT
# =========================================================

class AgentUpdateView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser
    ]

    def put(self, request, agent_id):

        try:

            user = User.objects.select_related(
                "agent_profile"
            ).get(
                id=agent_id,
                agent_profile__isnull=False
            )

        except User.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Agent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = AgentUpdateSerializer(
            user,
            data=request.data
        )

        if serializer.is_valid():

            serializer.save()

            return Response(
                {
                    "success": True,
                    "message": "Agent updated successfully.",
                    "agent": AgentSerializer(
                        user
                    ).data
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {
                "success": False,
                "errors": serializer.errors
            },
            status=status.HTTP_400_BAD_REQUEST
        )


# =========================================================
# DELETE AGENT
# =========================================================

class AgentDeleteView(APIView):

    permission_classes = [
        IsAuthenticated,
        IsAdminUser
    ]

    def delete(self, request, agent_id):

        try:

            user = User.objects.get(
                id=agent_id,
                agent_profile__isnull=False
            )

        except User.DoesNotExist:

            return Response(
                {
                    "success": False,
                    "message": "Agent not found."
                },
                status=status.HTTP_404_NOT_FOUND
            )

        username = user.username

        user.delete()

        return Response(
            {
                "success": True,
                "message":
                    f"Agent '{username}' deleted successfully."
            },
            status=status.HTTP_200_OK
        )