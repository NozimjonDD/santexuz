from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from apps.users.models import User
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from apps.common.authentication import active_user_rule, require_preview_boundary


class ApplicationTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        token = self.token_class(attrs["refresh"])
        user = User.objects.filter(pk=token.get("user_id")).first()
        if not active_user_rule(user):
            raise AuthenticationFailed("Account is inactive or deleted.")
        require_preview_boundary(user, self.context["request"])
        return super().validate(attrs)


class TelegramLoginSerializer(serializers.Serializer):
    init_data = serializers.CharField(max_length=16384, trim_whitespace=False)
    language = serializers.ChoiceField(choices=["uz", "ru", "en"], default="uz")


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "role", "language", "phone_number", "phone_verified_at", "is_staff"]
        read_only_fields = ["id", "role", "phone_number", "phone_verified_at", "is_staff"]


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class LoginResponseSerializer(serializers.Serializer):
    access = serializers.CharField()
    refresh = serializers.CharField()
    user = ProfileSerializer()
