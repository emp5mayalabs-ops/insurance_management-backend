# customer_portal/views.py
from django.contrib.auth.models import User
from django.db.models import Q

from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from rest_framework_simplejwt.tokens import RefreshToken

from customer_portal.models import CustomerProfile
from customer_portal.serializers import (
    CustomerCreateSerializer,
    CustomerSerializer,
    CustomerLoginSerializer,
    CustomerUpdateSerializer,
)


# =========================================================
# HELPER — require the caller to be an agent or admin
# =========================================================

def _is_agent(user):
    return hasattr(user, "agent_profile") or user.is_superuser


def _get_customer_profile(customer_id, user):
    """
    Retrieve CustomerProfile matching customer_id (which could be user.id or CustomerProfile.id).
    If caller is an agent (and not superuser), restrict to customers created by that agent.
    """
    qs = CustomerProfile.objects.select_related("user", "created_by_agent")
    if not user.is_superuser:
        qs = qs.filter(created_by_agent=user)
    return qs.get(Q(user_id=customer_id) | Q(id=customer_id))


# =========================================================
# CREATE CUSTOMER  (AGENT-ONLY)
# =========================================================

class CreateCustomerView(APIView):

    permission_classes = [IsAuthenticated]

    def post(self, request):

        # Only an agent can create a customer
        if not _is_agent(request.user):
            return Response(
                {
                    "success": False,
                    "message": "Only agents can create customers."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        if not request.user.is_superuser and not request.user.agent_profile.is_active:
            return Response(
                {
                    "success": False,
                    "message": "Your agent account is inactive."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = CustomerCreateSerializer(
            data=request.data,
            context={"agent_user": request.user},
        )

        if serializer.is_valid():

            user = serializer.save()
            profile = user.customer_profile

            return Response(
                {
                    "success": True,
                    "message": "Customer created successfully.",
                    "customer": CustomerSerializer(profile).data,
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
# LIST CUSTOMERS OF THE LOGGED-IN AGENT
# =========================================================

class CustomerListView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        if not _is_agent(request.user):
            return Response(
                {
                    "success": False,
                    "message": "Only agents can view their customers."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        qs = CustomerProfile.objects.all()
        if not request.user.is_superuser:
            qs = qs.filter(created_by_agent=request.user)

        customers = qs.select_related(
            "user",
            "created_by_agent",
        ).order_by("-id")

        serializer = CustomerSerializer(customers, many=True)

        return Response(
            {
                "success": True,
                "count": customers.count(),
                "customers": serializer.data,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# GET SINGLE CUSTOMER (AGENT-ONLY — their own)
# =========================================================

class CustomerDetailView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request, customer_id):

        if not _is_agent(request.user):
            return Response(
                {"success": False, "message": "Agent access required."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = _get_customer_profile(customer_id, request.user)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        return Response(
            {
                "success": True,
                "customer": CustomerSerializer(profile).data,
            },
            status=status.HTTP_200_OK
        )

    def put(self, request, customer_id):
        return CustomerUpdateView().put(request, customer_id)

    def patch(self, request, customer_id):
        return CustomerUpdateView().patch(request, customer_id)

    def delete(self, request, customer_id):
        return CustomerDeleteView().delete(request, customer_id)


# =========================================================
# UPDATE CUSTOMER (AGENT-ONLY — their own)
# =========================================================

class CustomerUpdateView(APIView):

    permission_classes = [IsAuthenticated]

    def put(self, request, customer_id):

        if not _is_agent(request.user):
            return Response(
                {"success": False, "message": "Agent access required."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = _get_customer_profile(customer_id, request.user)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = CustomerUpdateSerializer(
            instance=profile.user,
            data=request.data,
            partial=True,
        )

        if serializer.is_valid():
            serializer.save()

            # Refresh the profile from DB so the response shows new values
            profile.refresh_from_db()

            return Response(
                {
                    "success": True,
                    "message": "Customer updated successfully.",
                    "customer": CustomerSerializer(profile).data,
                },
                status=status.HTTP_200_OK
            )

        return Response(
            {"success": False, "errors": serializer.errors},
            status=status.HTTP_400_BAD_REQUEST
        )

    def patch(self, request, customer_id):
        return self.put(request, customer_id)


# =========================================================
# DELETE CUSTOMER (AGENT-ONLY — their own)
# =========================================================

class CustomerDeleteView(APIView):

    permission_classes = [IsAuthenticated]

    def delete(self, request, customer_id):

        if not _is_agent(request.user):
            return Response(
                {"success": False, "message": "Agent access required."},
                status=status.HTTP_403_FORBIDDEN
            )

        try:
            profile = _get_customer_profile(customer_id, request.user)
        except CustomerProfile.DoesNotExist:
            return Response(
                {"success": False, "message": "Customer not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        username = profile.user.username
        profile.user.delete()

        return Response(
            {
                "success": True,
                "message": f"Customer '{username}' deleted successfully.",
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# CUSTOMER LOGIN
# =========================================================

class CustomerLoginView(APIView):

    permission_classes = []

    def post(self, request):

        if not isinstance(request.data, dict):
            return Response(
                {
                    "success": False,
                    "message": "Invalid request body. Send JSON.",
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = CustomerLoginSerializer(
            data=request.data,
            context={"request": request},
        )

        if not serializer.is_valid():
            return Response(
                {
                    "success": False,
                    "errors": serializer.errors,
                },
                status=status.HTTP_401_UNAUTHORIZED
            )

        user = serializer.validated_data["user"]

        refresh = RefreshToken.for_user(user)
        refresh["role"] = "customer"
        refresh["customer_id"] = user.customer_profile.customer_id
        refresh["username"] = user.username

        return Response(
            {
                "success": True,
                "message": "Customer login successful.",
                "access": str(refresh.access_token),
                "refresh": str(refresh),
                "customer": CustomerSerializer(
                    user.customer_profile
                ).data,
            },
            status=status.HTTP_200_OK
        )


# =========================================================
# CUSTOMER "ME"
# =========================================================

class CustomerMeView(APIView):

    permission_classes = [IsAuthenticated]

    def get(self, request):

        user = request.user

        if not hasattr(user, "customer_profile"):
            return Response(
                {
                    "success": False,
                    "message": "This account is not a customer account.",
                },
                status=status.HTTP_403_FORBIDDEN
            )

        return Response(
            {
                "success": True,
                "customer": CustomerSerializer(
                    user.customer_profile
                ).data,
            },
            status=status.HTTP_200_OK
        )