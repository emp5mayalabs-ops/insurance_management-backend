# admin_portal/urls.py
from django.urls import path

from .views import (
    AdminLoginView,
    CreateAgentView,
    AgentListView,
    AgentDetailView,
    AgentUpdateView,
    AgentDeleteView,
)


urlpatterns = [

    # ---------------------------------------------------
    # ADMIN LOGIN
    # POST /api/admin/login/
    # ---------------------------------------------------
    path(
        "login/",
        AdminLoginView.as_view(),
        name="admin-login"
    ),

    # ---------------------------------------------------
    # CREATE AGENT
    # POST /api/admin/agents/create/
    # ---------------------------------------------------
    path(
        "agents/create/",
        CreateAgentView.as_view(),
        name="create-agent"
    ),

    # ---------------------------------------------------
    # VIEW ALL AGENTS
    # GET /api/admin/agents/
    # ---------------------------------------------------
    path(
        "agents/",
        AgentListView.as_view(),
        name="agent-list"
    ),

    # ---------------------------------------------------
    # VIEW ONE AGENT
    # GET /api/admin/agents/<id>/
    # ---------------------------------------------------
    path(
        "agents/<int:agent_id>/",
        AgentDetailView.as_view(),
        name="agent-detail"
    ),

    # ---------------------------------------------------
    # EDIT AGENT
    # PUT /api/admin/agents/<id>/update/
    # ---------------------------------------------------
    path(
        "agents/<int:agent_id>/update/",
        AgentUpdateView.as_view(),
        name="agent-update"
    ),

    # ---------------------------------------------------
    # DELETE AGENT
    # DELETE /api/admin/agents/<id>/delete/
    # ---------------------------------------------------
    path(
        "agents/<int:agent_id>/delete/",
        AgentDeleteView.as_view(),
        name="agent-delete"
    ),
]