from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

# from apps.client.models import Client
from apps.users import models
# from apps.client import models as client_models
# from apps.business.models import Specialist
from apps.common.choices import UserOTPTypes, UserRoleTypes
from . import fields as custom_fields


class LoginSerializer(serializers.ModelSerializer):
    phone_number = custom_fields.PhoneNumberField()
    secret = serializers.CharField(max_length=50, read_only=True)
    role = serializers.ChoiceField(
        choices=[UserRoleTypes.ORDINARY, UserRoleTypes.BUSINESS], default=UserRoleTypes.ORDINARY
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.action_type = UserOTPTypes.OTHER

    class Meta:
        model = models.User
        fields = (
            "role",
            "phone_number",
            "secret",
        )

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")
        self.action_type = UserOTPTypes.LOGIN

        try:
            user = models.User.objects.get(phone_number=phone_number)
        except models.User.DoesNotExist:
            self.action_type = UserOTPTypes.REGISTER
            return attrs

        if not user.is_active:
            self.action_type = UserOTPTypes.REGISTER
            return attrs

        if attrs["role"] != user.role:
            raise serializers.ValidationError(
                code="invalid_role",
                detail={"role": [_("This phone number is belongs to another role!")]}
            )

        return attrs

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]

        if self.action_type == UserOTPTypes.LOGIN:
            user = models.User.objects.get(phone_number=phone_number)
        else:

            try:
                user = models.User.objects.get(phone_number=phone_number)
            except models.User.DoesNotExist:
                user = models.User.objects.create(
                    phone_number=phone_number,
                    is_active=False,
                    role=validated_data["role"],
                )
            if validated_data["role"] == UserRoleTypes.ORDINARY:
                client, _ = Client.objects.get_or_create(
                    user=user,
                )
            elif validated_data["role"] == UserRoleTypes.BUSINESS:
                specialist, _ = Specialist.objects.get_or_create(
                    user=user,
                )
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        otp = instance.generate_otp(typ=self.action_type)
        data["secret"] = otp.secret

        return data


class LoginConfirmSerializer(serializers.ModelSerializer):
    secret = serializers.CharField(max_length=100, write_only=True)
    otp = serializers.CharField(
        max_length=10,
        min_length=4,
        error_messages={
            "min_length": _("OTP must be at least 4 characters long."),
            "max_length": _("OTP must be at most 10 characters long."),
        },
        write_only=True
    )

    class Meta:
        model = models.User
        fields = (
            "id",
            "phone_number",
            "secret",
            "otp",
        )
        extra_kwargs = {
            "phone_number": {"read_only": True},
        }

    def validate(self, attrs):
        secret = attrs.get("secret")
        otp = attrs.get("otp")

        try:
            user_otp = models.UserOTP.objects.get(
                secret=secret,
                type__in=[UserOTPTypes.LOGIN, UserOTPTypes.REGISTER],
                is_confirmed=False,
                user__is_deleted=False,
            )
        except models.UserOTP.DoesNotExist:
            raise serializers.ValidationError(
                code="invalid_secret",
                detail={
                    "secret": [_("Invalid secret.")]
                }
            )

        if user_otp.is_expired():
            raise serializers.ValidationError(
                code="expired_otp",
                detail={
                    "otp": [_("OTP is expired.")]
                }
            )

        if user_otp.code != otp:
            raise serializers.ValidationError(
                code="invalid_otp",
                detail={
                    "otp": [_("Invalid OTP.")]
                }
            )
        return attrs

    def create(self, validated_data):
        user_otp = models.UserOTP.objects.get(secret=validated_data["secret"])
        user = user_otp.user
        user_otp.confirm()

        if user_otp.type == UserOTPTypes.REGISTER:
            user.is_active = True
            user.save()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token_data = instance.generate_refresh_token()
        data["access"] = token_data["access"]
        data["refresh"] = token_data["refresh"]
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    phone_number = custom_fields.PhoneNumberField()
    secret = serializers.CharField(max_length=50, read_only=True)

    class Meta:
        model = models.User
        fields = (
            "phone_number",
            "secret",
        )

    def validate(self, attrs):
        phone_number = attrs.get("phone_number")

        if models.User.objects.filter(phone_number=phone_number, is_active=True).exists():
            raise serializers.ValidationError(
                code="already_exists",
                detail={
                    "phone_number": [_("A user with that phone number already exists.")]
                }
            )
        return attrs

    def create(self, validated_data):
        phone_number = validated_data["phone_number"]
        try:
            user = models.User.objects.get(phone_number=phone_number)
        except models.User.DoesNotExist:
            validated_data["role"] = UserRoleTypes.ORDINARY
            validated_data["is_active"] = False
            user = super().create(validated_data=validated_data)
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        otp = instance.generate_otp(typ=UserOTPTypes.REGISTER)
        data["secret"] = otp.secret
        return data


class UserRegisterConfirmSerializer(serializers.ModelSerializer):
    secret = serializers.CharField(max_length=100, write_only=True)
    otp = serializers.CharField(
        max_length=10,
        min_length=4,
        error_messages={
            "min_length": _("OTP must be at least 4 characters long."),
            "max_length": _("OTP must be at most 10 characters long."),
        },
        write_only=True
    )

    class Meta:
        model = models.User
        fields = (
            "id",
            "phone_number",
            "secret",
            "otp",
        )
        extra_kwargs = {
            "phone_number": {"read_only": True},
        }

    def validate(self, attrs):
        secret = attrs.get("secret")
        otp = attrs.get("otp")

        try:
            user_otp = models.UserOTP.objects.get(
                secret=secret,
                type=UserOTPTypes.REGISTER,
                is_confirmed=False,
                user__is_deleted=False,
            )
        except models.UserOTP.DoesNotExist:
            raise serializers.ValidationError(
                code="invalid_secret",
                detail={
                    "secret": [_("Invalid secret.")]
                }
            )

        if user_otp.is_expired():
            raise serializers.ValidationError(
                code="expired_otp",
                detail={
                    "otp": [_("OTP is expired.")]
                }
            )

        if user_otp.code != otp:
            raise serializers.ValidationError(
                code="invalid_otp",
                detail={
                    "otp": [_("Invalid OTP.")]
                }
            )
        return attrs

    def create(self, validated_data):

        user_otp = models.UserOTP.objects.get(secret=validated_data["secret"])
        user = user_otp.user
        user.is_active = True
        user.date_joined = timezone.now()
        user.save(update_fields=["is_active", "date_joined"])

        # if not hasattr(user, "client"):
        #     client_models.Client.objects.create(user=user)

        user_otp.confirm()
        return user

    def to_representation(self, instance):
        data = super().to_representation(instance)
        token_data = instance.generate_refresh_token()
        data["access"] = token_data["access"]
        data["refresh"] = token_data["refresh"]
        return data
