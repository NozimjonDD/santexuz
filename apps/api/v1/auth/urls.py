from django.urls import path
from django.conf import settings
from rest_framework_simplejwt.views import TokenRefreshView
from .views import LogoutView, ProfileView, StaffLoginView, TelegramLoginView
from .notifications import NotificationListView, NotificationReadView

urlpatterns = [
    path("telegram/", TelegramLoginView.as_view(), name="telegram-login"),
    path("staff/", StaffLoginView.as_view(), name="staff-login"),
    path("refresh/", TokenRefreshView.as_view(), name="token-refresh"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("me/", ProfileView.as_view(), name="profile"),
    path("notifications/", NotificationListView.as_view(), name="notification-list"),
    path("notifications/<int:pk>/read/", NotificationReadView.as_view(), name="notification-read"),
]

if settings.DEBUG and getattr(settings, "DEV_LOCAL_LOGIN", False):
    from .development import LocalPreviewLoginView
    urlpatterns += [path("dev-local/", LocalPreviewLoginView.as_view(), name="dev-local-login")]
