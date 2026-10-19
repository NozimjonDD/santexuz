from rest_framework import serializers
from decimal import Decimal, ROUND_HALF_UP
from django.db.models import Avg
from drf_spectacular.utils import extend_schema_serializer

from apps.catalog.models import Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.users.models import PlumberProfile, Store
from apps.orders.models import Rating


def public_rating(obj, partner):
    if hasattr(obj, "rating"):
        value = obj.rating
    else:
        value = Rating.objects.filter(approved=True, is_deleted=False, order__is_deleted=False, **{f"order__{partner}_id": obj.user_id}).aggregate(value=Avg(f"{partner}_score"))["value"]
    return format(Decimal(str(value)).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP), ".2f") if value is not None else None


@extend_schema_serializer(component_name="PublicRegion")
class RegionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Region
        fields = ("id", "name", "code")


@extend_schema_serializer(component_name="PublicServiceGroup")
class ServiceGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceGroup
        fields = ("id", "name", "name_ru", "name_en", "code")


@extend_schema_serializer(component_name="PublicService")
class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = ("id", "group", "name", "name_ru", "name_en", "unit", "warranty_days")


@extend_schema_serializer(component_name="PublicServiceRate")
class ServiceRateSerializer(serializers.ModelSerializer):
    service = ServiceSerializer(read_only=True)

    class Meta:
        model = ServiceRate
        fields = ("id", "region", "service", "unit_price", "urgent_fee")


@extend_schema_serializer(component_name="PublicMaterial")
class MaterialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Material
        fields = ("id", "name", "unit", "brand")


@extend_schema_serializer(component_name="PublicServiceCenter")
class ServiceCenterSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCenter
        fields = ("id", "name", "address", "phone", "opening_time", "closing_time", "working_days")


class PublicPlumberSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    photo = serializers.SerializerMethodField()
    services = serializers.SerializerMethodField()
    regions = serializers.SerializerMethodField()
    rating = serializers.SerializerMethodField()

    def get_services(self, obj) -> list:
        visible = [item for item in obj.services.all() if item.is_active and not item.is_deleted]
        return ServiceGroupSerializer(visible, many=True).data

    def get_regions(self, obj) -> list[int]:
        return [item.pk for item in obj.regions.all() if item.is_active and not item.is_deleted]

    def get_rating(self, obj) -> str | None:
        return public_rating(obj, "plumber")

    def get_name(self, obj) -> str:
        return obj.user.get_full_name() or obj.user.username

    def get_photo(self, obj) -> str | None:
        return f"/api/v1/common/plumbers/{obj.pk}/photo/" if obj.photo else None

    class Meta:
        model = PlumberProfile
        fields = ("id", "name", "photo", "experience_years", "regions", "services", "rating")


class PublicStoreSerializer(serializers.ModelSerializer):
    rating = serializers.SerializerMethodField()

    def get_rating(self, obj) -> str | None:
        return public_rating(obj, "store")

    class Meta:
        model = Store
        fields = ("id", "name", "address", "rating")


class PublicReviewSerializer(serializers.ModelSerializer):
    score = serializers.SerializerMethodField()

    def get_score(self, obj) -> int:
        return getattr(obj, self.context["score_field"])

    class Meta:
        model = Rating
        fields = ("id", "score", "comment", "created_at")
