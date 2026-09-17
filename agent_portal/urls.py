# agent_portal/urls.py
from django.urls import path

from agent_portal.views import AgentLoginView, AgentMeView


urlpatterns = [
    path("login/", AgentLoginView.as_view(), name="agent-login"),
    path("me/", AgentMeView.as_view(), name="agent-me"),
]