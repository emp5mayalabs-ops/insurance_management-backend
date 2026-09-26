# customer_portal/urls.py
from django.urls import path

from customer_portal.views import (
    CreateCustomerView,
    CustomerListView,
    CustomerDetailView,
    CustomerUpdateView,
    CustomerDeleteView,
    CustomerLoginView,
    CustomerMeView,
)


urlpatterns = [

    # =========================================================
    # AGENT-FACING — FIXED ROUTES FIRST
    # (must come before <int:customer_id> or they'd be shadowed)
    # =========================================================
    path(
        "customers/create/",
        CreateCustomerView.as_view(),
        name="customer-create"
    ),
    path(
        "customers/",
        CustomerListView.as_view(),
        name="customer-list"
    ),

    # =========================================================
    # AGENT-FACING — DYNAMIC ROUTES (by numeric User.id)
    # =========================================================
    path(
        "customers/<int:customer_id>/",
        CustomerDetailView.as_view(),
        name="customer-detail"
    ),
    path(
        "customers/<int:customer_id>/update/",
        CustomerUpdateView.as_view(),
        name="customer-update"
    ),
    path(
        "customers/<int:customer_id>/delete/",
        CustomerDeleteView.as_view(),
        name="customer-delete"
    ),

    # =========================================================
    # CUSTOMER-FACING
    # =========================================================
    path(
        "customer/login/",
        CustomerLoginView.as_view(),
        name="customer-login"
    ),
    path(
        "customer/me/",
        CustomerMeView.as_view(),
        name="customer-me"
    ),
]