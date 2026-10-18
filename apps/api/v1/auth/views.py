from django.db import transaction
from rest_framework import generics, permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.throttling import ScopedRateThrottle
from rest_framework_simplejwt.exceptions import TokenError
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_spectacular.utils import extend_schema

from apps.common.audit import record
from .serializers import LoginResponseSerializer, LogoutSerializer, ProfileSerializer, TelegramLoginSerializer
from .services import telegram_login


class TelegramLoginView(generics.GenericAPIView):
    permission_classes = [permissions.AllowAny]
    authentication_classes = []
    serializer_class = TelegramLoginSerializer
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def get_authenticate_header(self, request):
        return "Bearer"

    @extend_schema(request=TelegramLoginSerializer, responses=LoginResponseSerializer)
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = telegram_login(serializer.validated_data["init_data"], serializer.validated_data["language"])
        token = RefreshToken.for_user(user)
        return Response({"access": str(token.access_token), "refresh": str(token), "user": ProfileSerializer(user).data})


class StaffLoginView(TokenObtainPairView):
    throttle_classes = [ScopedRateThrottle]
    throttle_scope = "login"

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        if not serializer.user.is_staff:
            raise ValidationError("Staff account required.")
        record(serializer.user, "auth.staff_login", serializer.user)
        return Response(serializer.validated_data)


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = ProfileSerializer
    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user

    @transaction.atomic
    def perform_update(self, serializer):
        user = serializer.save()
        record(user, "auth.profile_updated", user)


class LogoutView(generics.GenericAPIView):
    serializer_class = LogoutSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            token = RefreshToken(serializer.validated_data["refresh"])
            if str(token["user_id"]) != str(request.user.pk):
                raise ValidationError("Token belongs to another account.")
            token.blacklist()
        except TokenError as exc:
            raise ValidationError("Invalid refresh token.") from exc
        return Response(status=204)
