from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.authentication import SessionAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from apps.common.permissions import IsStaff

docs_access = {"authentication_classes": (JWTAuthentication, SessionAuthentication), "permission_classes": (IsStaff,)}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include("apps.api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(**docs_access), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema", **docs_access), name="swagger-ui"),
    path("telegram/webhook/", include("apps.tg_bot.urls")),
    path("", include("apps.common.urls")),
]
