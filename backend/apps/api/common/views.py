from django.db.models import Avg, Q
from django.http import FileResponse, Http404
import mimetypes
from rest_framework.decorators import action
from rest_framework import generics, permissions, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema

from apps.api.common import serializers
from apps.catalog.models import Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.users.models import PlumberProfile, Store
from apps.orders.models import Rating


def positive_query_id(request, name, required=False):
    value = request.query_params.get(name)
    if value is None:
        if required:
            raise ValidationError({name: "This query parameter is required."})
        return None
    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError({name: "A positive integer is required."})
    if value <= 0:
        raise ValidationError({name: "A positive integer is required."})
    return value


class PublicCatalogViewSet(viewsets.ReadOnlyModelViewSet):
    # Public projections never depend on the caller's (possibly expired) JWT.
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    http_method_names = ("get", "head", "options")

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)


class RegionViewSet(PublicCatalogViewSet):
    serializer_class = serializers.RegionSerializer
    queryset = Region.objects.filter(is_active=True)


class ServiceGroupViewSet(PublicCatalogViewSet):
    serializer_class = serializers.ServiceGroupSerializer
    queryset = ServiceGroup.objects.filter(is_active=True)


class ServiceViewSet(PublicCatalogViewSet):
    serializer_class = serializers.ServiceSerializer
    queryset = Service.objects.filter(is_active=True, group__is_active=True, group__is_deleted=False)

    def get_queryset(self):
        queryset = super().get_queryset()
        group_id = positive_query_id(self.request, "group")
        return queryset.filter(group_id=group_id) if group_id else queryset


class ServiceRateViewSet(PublicCatalogViewSet):
    serializer_class = serializers.ServiceRateSerializer
    queryset = ServiceRate.objects.select_related("service").filter(
        region__is_active=True, region__is_deleted=False, service__is_active=True, service__is_deleted=False,
        service__group__is_active=True, service__group__is_deleted=False,
    ).order_by("id")

    def get_queryset(self):
        queryset = super().get_queryset()
        region_id = positive_query_id(self.request, "region", required=True)
        queryset = queryset.filter(region_id=region_id)
        group_id = positive_query_id(self.request, "group")
        return queryset.filter(service__group_id=group_id) if group_id else queryset


class MaterialViewSet(PublicCatalogViewSet):
    serializer_class = serializers.MaterialSerializer
    queryset = Material.objects.filter(is_active=True)

    def get_queryset(self):
        queryset = super().get_queryset()
        search = self.request.query_params.get("search", "").strip()[:200]
        return queryset.filter(Q(name__icontains=search) | Q(brand__icontains=search)) if search else queryset


class ServiceCenterView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    serializer_class = serializers.ServiceCenterSerializer

    def get(self, request):
        center = ServiceCenter.objects.filter(pk=1, is_deleted=False).first()
        return Response(serializers.ServiceCenterSerializer(center).data if center else None)


class PlumberViewSet(PublicCatalogViewSet):
    serializer_class = serializers.PublicPlumberSerializer
    queryset = PlumberProfile.objects.filter(is_active=True, user__is_active=True, user__is_deleted=False).select_related("user").prefetch_related("regions", "services")

    def get_queryset(self):
        queryset = super().get_queryset().annotate(
            rating=Avg("user__plumber_orders__rating__plumber_score", filter=Q(user__plumber_orders__rating__approved=True, user__plumber_orders__rating__is_deleted=False, user__plumber_orders__is_deleted=False)),
        )
        region_id = positive_query_id(self.request, "region")
        group_id = positive_query_id(self.request, "group")
        if region_id:
            queryset = queryset.filter(regions__id=region_id)
        if group_id:
            queryset = queryset.filter(services__id=group_id)
        return queryset.distinct()

    @action(detail=True, methods=["get"])
    @extend_schema(responses={(200, "image/jpeg"): bytes, (200, "image/png"): bytes, (200, "image/webp"): bytes})
    def photo(self, request, pk=None):
        plumber = self.get_object()
        if not plumber.photo:
            raise Http404("Photo unavailable.")
        try:
            photo = plumber.photo.open("rb")
        except (FileNotFoundError, OSError):
            raise Http404("Photo unavailable.")
        content_type = mimetypes.guess_type(plumber.photo.name)[0]
        if content_type not in {"image/jpeg", "image/png", "image/webp"}:
            photo.close()
            raise Http404("Photo unavailable.")
        response = FileResponse(photo, content_type=content_type)
        response["Content-Disposition"] = "inline"
        response["X-Content-Type-Options"] = "nosniff"
        return response

    @action(detail=True, methods=["get"])
    @extend_schema(responses=serializers.PublicReviewSerializer(many=True))
    def reviews(self, request, pk=None):
        plumber = self.get_object()
        reviews = Rating.objects.filter(approved=True, is_deleted=False, order__is_deleted=False, order__plumber=plumber.user).order_by("-created_at", "-pk")
        page = self.paginate_queryset(reviews)
        data = serializers.PublicReviewSerializer(page, many=True, context={"score_field": "plumber_score"}).data
        return self.get_paginated_response(data)


class StoreViewSet(PublicCatalogViewSet):
    serializer_class = serializers.PublicStoreSerializer
    queryset = Store.objects.filter(is_active=True, user__is_active=True, user__is_deleted=False)

    def get_queryset(self):
        return super().get_queryset().annotate(
            rating=Avg("user__store_orders__rating__store_score", filter=Q(user__store_orders__rating__approved=True, user__store_orders__rating__is_deleted=False, user__store_orders__is_deleted=False)),
        )

    @action(detail=True, methods=["get"])
    @extend_schema(responses=serializers.PublicReviewSerializer(many=True))
    def reviews(self, request, pk=None):
        store = self.get_object()
        reviews = Rating.objects.filter(approved=True, is_deleted=False, order__is_deleted=False, order__store=store.user).order_by("-created_at", "-pk")
        page = self.paginate_queryset(reviews)
        data = serializers.PublicReviewSerializer(page, many=True, context={"score_field": "store_score"}).data
        return self.get_paginated_response(data)
