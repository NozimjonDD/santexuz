"""OpenAPI adapters for the application's custom JWT implementations."""
from drf_spectacular.contrib.rest_framework_simplejwt import (
    SimpleJWTScheme,
    TokenRefreshSerializerExtension,
)


class ApplicationJWTScheme(SimpleJWTScheme):
    target_class = "apps.common.authentication.ApplicationJWTAuthentication"
    priority = 1


class ApplicationRefreshSchema(TokenRefreshSerializerExtension):
    target_class = "apps.api.v1.auth.serializers.ApplicationTokenRefreshSerializer"
    priority = 1
