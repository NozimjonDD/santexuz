from django.urls import path
from .views import MiniAppView
from . import health

app_name = "common"
urlpatterns = [
    path("health/live/", health.live, name="health-live"),
    path("health/ready/", health.ready, name="health-ready"),
    path("", MiniAppView.as_view(), name="home"),
]
