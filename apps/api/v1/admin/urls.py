from django.urls import path, include

from apps.api.v1.admin import views

urlpatterns = [
    path("example/", views.MyAPIView.as_view(), name="example"),
]
