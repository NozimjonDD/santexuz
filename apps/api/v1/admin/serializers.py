"""Staff-only write contracts with explicit writable fields."""

from django.contrib.auth import get_user_model, password_validation
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import transaction
from rest_framework import serializers

from apps.api.v1.site.inputs import StrictSerializer
from apps.catalog.models import ContractTemplate, Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.common.audit import AuditEvent
from apps.users.models import PlumberProfile, Store

User = get_user_model()


class ValidatedModelSerializer(serializers.ModelSerializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("JSON object expected.")
        unknown = set(data) - set(self.fields)
        readonly = {key for key in data if key in self.fields and self.fields[key].read_only}
        if unknown or readonly:
            raise serializers.ValidationError({key: "Unknown or read-only field." for key in unknown | readonly})
        return super().to_internal_value(data)

    def validate(self, attrs):
        candidate = self.Meta.model()
        if self.instance:
            for field in self.Meta.model._meta.concrete_fields:
                setattr(candidate, field.attname, getattr(self.instance, field.attname))
        for name, value in attrs.items():
            if not self.Meta.model._meta.get_field(name).many_to_many:
                setattr(candidate, name, value)
        try:
            candidate.clean()
        except DjangoValidationError as exc:
            raise serializers.ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
        return attrs


class RegionSerializer(ValidatedModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name", "code", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceGroupSerializer(ValidatedModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ("id", "name", "name_ru", "name_en", "code", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceSerializer(ValidatedModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "group", "name", "name_ru", "name_en", "unit", "warranty_days", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceRateSerializer(ValidatedModelSerializer):
    class Meta:
        model = ServiceRate
        fields = ("id", "region", "service", "unit_price", "urgent_fee", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class MaterialSerializer(ValidatedModelSerializer):
    class Meta:
        model = Material
        fields = ("id", "name", "unit", "brand", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class ServiceCenterSerializer(ValidatedModelSerializer):
    class Meta:
        model = ServiceCenter
        fields = (
            "id", "name", "address", "phone", "opening_time", "closing_time", "working_days",
            "default_plumber_commission", "default_store_commission", "advance_kind", "advance_value",
            "plumber_response_minutes", "created_at", "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")


class ContractTemplateSerializer(ValidatedModelSerializer):
    class Meta:
        model = ContractTemplate
        fields = ("id", "language", "version", "text", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")


class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, trim_whitespace=False, max_length=128)

    class Meta:
        model = User
        fields = (
            "id", "username", "password", "telegram_id", "first_name", "last_name", "phone_number",
            "phone_verified_at", "language", "role", "is_active", "is_staff", "date_joined",
        )
        read_only_fields = ("id", "phone_verified_at", "date_joined")

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("JSON object expected.")
        unknown = set(data) - set(self.fields)
        readonly = {key for key in data if key in self.fields and self.fields[key].read_only}
        if unknown or readonly:
            raise serializers.ValidationError({key: "Unknown or read-only field." for key in unknown | readonly})
        return super().to_internal_value(data)

    def validate(self, attrs):
        if self.instance and self.instance.is_superuser:
            raise serializers.ValidationError("Superuser accounts are managed outside the CRM.")
        if self.instance and self.instance.pk == self.context["request"].user.pk:
            if attrs.get("is_active") is False or attrs.get("is_staff") is False:
                raise serializers.ValidationError("You cannot disable your own staff access.")
        password = attrs.get("password")
        if password is not None:
            candidate = User(username=attrs.get("username", getattr(self.instance, "username", "")))
            try:
                password_validation.validate_password(password, candidate)
            except DjangoValidationError as exc:
                raise serializers.ValidationError({"password": exc.messages})
        if self.instance and attrs.get("role", self.instance.role) != self.instance.role:
            # Reclassifying users with historical orders breaks participant policy.
            raise serializers.ValidationError({"role": "Create a separate partner account instead of changing an existing role."})
        return attrs

    def create(self, validated_data):
        password = validated_data.pop("password", None)
        return User.objects.create_user(password=password, **validated_data)

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        # The verified Telegram contact cannot survive a manually edited number.
        if "phone_number" in validated_data and validated_data["phone_number"] != instance.phone_number:
            instance.phone_verified_at = None
        if "telegram_id" in validated_data and validated_data["telegram_id"] != instance.telegram_id:
            instance.phone_verified_at = None
        for name, value in validated_data.items():
            setattr(instance, name, value)
        if password is not None:
            instance.set_password(password)
        instance.save()
        return instance


class PlumberProfileSerializer(ValidatedModelSerializer):
    photo = serializers.ImageField(required=False, allow_empty_file=False)

    class Meta:
        model = PlumberProfile
        fields = ("id", "user", "regions", "services", "commission_rate", "experience_years", "photo", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_user(self, user):
        if self.instance and self.instance.user_id != user.pk:
            raise serializers.ValidationError("Existing partner profile cannot be reassigned to another account.")
        if user.role != User.Role.PLUMBER or user.is_staff:
            raise serializers.ValidationError("A plumber account is required.")
        return user

    def validate_photo(self, photo):
        if photo.size > 5 * 1024 * 1024:
            raise serializers.ValidationError("Photo must be at most 5 MB.")
        if getattr(photo, "content_type", "") not in {"image/jpeg", "image/png", "image/webp"}:
            raise serializers.ValidationError("Use a JPEG, PNG or WebP photo.")
        return photo


class StoreSerializer(ValidatedModelSerializer):
    class Meta:
        model = Store
        fields = ("id", "user", "name", "address", "latitude", "longitude", "commission_rate", "is_active", "created_at", "updated_at")
        read_only_fields = ("id", "created_at", "updated_at")

    def validate_user(self, user):
        if self.instance and self.instance.user_id != user.pk:
            raise serializers.ValidationError("Existing store cannot be reassigned to another account.")
        if user.role != User.Role.STORE or user.is_staff:
            raise serializers.ValidationError("A store account is required.")
        return user


class AuditEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = AuditEvent
        fields = ("id", "actor", "action", "object_type", "object_id", "payload", "created_at")
        read_only_fields = fields
