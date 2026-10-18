from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.contrib.auth.backends import ModelBackend

from .development import local_preview_enabled


def active_user_rule(user):
    return bool(user is not None and user.is_active and not user.is_deleted)


class ActiveUserBackend(ModelBackend):
    def user_can_authenticate(self, user):
        return active_user_rule(user)


def require_preview_boundary(user, request):
    if user.email == "local-preview@invalid.example" and not local_preview_enabled(request):
        raise AuthenticationFailed("Local preview account is available only in local development.")


class ApplicationJWTAuthentication(JWTAuthentication):
    def get_user(self, validated_token):
        user = super().get_user(validated_token)
        if not active_user_rule(user):
            raise AuthenticationFailed("Account is inactive or deleted.")
        return user

    def authenticate(self, request):
        result = super().authenticate(request)
        if result is not None:
            require_preview_boundary(result[0], request)
        return result
