from django.urls import path
from .views import MiniAppView

app_name = "common"
urlpatterns = [path("", MiniAppView.as_view(), name="home")]
