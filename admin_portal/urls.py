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

    # Admin Login
    path(
        "login/",
        AdminLoginView.as_view(),
        name="admin-login"
    ),

    # Create Agent
    path(
        "agents/create/",
        CreateAgentView.as_view(),
        name="create-agent"
    ),

    # View All Agents
    path(
        "agents/",
        AgentListView.as_view(),
        name="agent-list"
    ),

    # View One Agent
    path(
        "agents/<int:agent_id>/",
        AgentDetailView.as_view(),
        name="agent-detail"
    ),

    # Edit Agent
    path(
        "agents/<int:agent_id>/update/",
        AgentUpdateView.as_view(),
        name="agent-update"
    ),

    # Delete Agent
    path(
        "agents/<int:agent_id>/delete/",
        AgentDeleteView.as_view(),
        name="agent-delete"
    ),
]