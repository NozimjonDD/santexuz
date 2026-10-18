import csv
from io import BytesIO

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import IntegrityError, transaction
from django.db.models.deletion import ProtectedError
from django.http import HttpResponse
from rest_framework import mixins, status, viewsets
from rest_framework import serializers as drf_serializers
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed, ValidationError
from rest_framework.response import Response
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, extend_schema_view

from apps.api.common.views import positive_query_id
from apps.api.v1.admin import serializers
from apps.api.v1.site import inputs
from apps.api.v1.site.serializers import OrderSerializer, monetary_projection
from apps.api.v1.site.views import OrderViewSet as ParticipantOrderViewSet
from apps.catalog.models import ContractTemplate, Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.common.audit import AuditEvent, record
from apps.common.permissions import IsStaff
from apps.orders import models, selectors
from apps.users.models import PlumberProfile, Store

User = get_user_model()


def django_error(exc):
    return ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)


class AuditedModelViewSet(viewsets.ModelViewSet):
    permission_classes = (IsStaff,)

    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def perform_create(self, serializer):
        try:
            with transaction.atomic():
                obj = serializer.save()
                record(self.request.user, "api.create", obj, {"fields": sorted(set(serializer.validated_data) - {"password"})})
        except DjangoValidationError as exc:
            raise django_error(exc)
        except IntegrityError:
            raise ValidationError("An object with these unique values already exists.")

    def perform_update(self, serializer):
        try:
            with transaction.atomic():
                obj = serializer.save()
                record(self.request.user, "api.update", obj, {"fields": sorted(set(serializer.validated_data) - {"password"})})
        except DjangoValidationError as exc:
            raise django_error(exc)
        except IntegrityError:
            raise ValidationError("This change conflicts with an existing object.")

    def perform_destroy(self, instance):
        try:
            with transaction.atomic():
                if hasattr(instance, "is_active"):
                    instance.is_active = False
                    instance.save()
                    record(self.request.user, "api.deactivate", instance)
                else:
                    record(self.request.user, "api.delete", instance)
                    instance.delete()
        except ProtectedError:
            raise ValidationError("This object is in use and cannot be deleted.")


class RegionViewSet(AuditedModelViewSet):
    queryset = Region.objects.all()
    serializer_class = serializers.RegionSerializer


class ServiceGroupViewSet(AuditedModelViewSet):
    queryset = ServiceGroup.objects.all()
    serializer_class = serializers.ServiceGroupSerializer


class ServiceViewSet(AuditedModelViewSet):
    queryset = Service.objects.select_related("group").all()
    serializer_class = serializers.ServiceSerializer


class ServiceRateViewSet(AuditedModelViewSet):
    queryset = ServiceRate.objects.select_related("region", "service").order_by("id")
    serializer_class = serializers.ServiceRateSerializer


class MaterialViewSet(AuditedModelViewSet):
    queryset = Material.objects.all()
    serializer_class = serializers.MaterialSerializer


class ContractTemplateViewSet(AuditedModelViewSet):
    queryset = ContractTemplate.objects.all()
    serializer_class = serializers.ContractTemplateSerializer


class UserViewSet(AuditedModelViewSet):
    queryset = User.objects.filter(is_superuser=False).order_by("id")
    serializer_class = serializers.UserSerializer

    def get_queryset(self):
        queryset = super().get_queryset()
        role = self.request.query_params.get("role")
        if role:
            if role not in User.Role.values:
                raise ValidationError({"role": "Unknown account role."})
            queryset = queryset.filter(role=role)
        return queryset

    def perform_destroy(self, instance):
        if instance.pk == self.request.user.pk:
            raise ValidationError("You cannot disable your own account.")
        return super().perform_destroy(instance)


class PlumberProfileViewSet(AuditedModelViewSet):
    queryset = PlumberProfile.objects.select_related("user").prefetch_related("regions", "services").order_by("id")
    serializer_class = serializers.PlumberProfileSerializer


class StoreViewSet(AuditedModelViewSet):
    queryset = Store.objects.select_related("user").order_by("id")
    serializer_class = serializers.StoreSerializer


class ServiceCenterView(APIView):
    permission_classes = (IsStaff,)
    serializer_class = serializers.ServiceCenterSerializer

    def get(self, request):
        center = ServiceCenter.objects.filter(pk=1).first()
        return Response(serializers.ServiceCenterSerializer(center).data if center else None)

    def put(self, request):
        return self._save(request, partial=False)

    def patch(self, request):
        return self._save(request, partial=True)

    def _save(self, request, partial):
        center = ServiceCenter.objects.filter(pk=1).first()
        serializer = serializers.ServiceCenterSerializer(center, data=request.data, partial=partial and center is not None)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                center = serializer.save()
                record(request.user, "api.center_update", center, {"fields": sorted(serializer.validated_data)})
        except DjangoValidationError as exc:
            raise django_error(exc)
        return Response(serializer.data)


class AuditEventViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = (IsStaff,)
    queryset = AuditEvent.objects.select_related("actor").all()
    serializer_class = serializers.AuditEventSerializer
    http_method_names = ("get", "head", "options")

    def get_queryset(self):
        queryset = super().get_queryset()
        actor_id = positive_query_id(self.request, "actor")
        if actor_id:
            queryset = queryset.filter(actor_id=actor_id)
        for name in ("object_type", "object_id", "action"):
            value = self.request.query_params.get(name)
            if value:
                queryset = queryset.filter(**{name: value[:100]})
        return queryset


class StaffOrderSerializer(OrderSerializer):
    financials = drf_serializers.SerializerMethodField()
    settlements = drf_serializers.SerializerMethodField()

    def get_financials(self, obj) -> dict:
        result = selectors.financial_summary(obj)
        quote = selectors.current_quote(obj)
        if quote:
            for key in ("plumber_rate", "store_rate", "plumber_commission", "store_commission"):
                result[key] = quote.snapshot.get(key, "0.00")
        return monetary_projection(result)

    def get_settlements(self, obj) -> list[dict]:
        return [monetary_projection({"id": item.pk, "partner": item.partner, "amount": item.amount,
                "recorded_by_id": item.recorded_by_id, "created_at": item.created_at}) for item in obj.settlements.all()]

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ("financials", "settlements", "refund_limit", "company_failure", "response_alerted_at")


@extend_schema_view(
    create=extend_schema(exclude=True),
    assign_plumber=extend_schema(request=inputs.AssignmentInput, responses=StaffOrderSerializer),
    assign_store=extend_schema(request=inputs.StoreAssignmentInput, responses=StaffOrderSerializer),
    confirm_urgent=extend_schema(request=inputs.UrgentInput, responses=StaffOrderSerializer),
    sign_contract=extend_schema(request=inputs.EmptyInput, responses=StaffOrderSerializer),
    resolve_dispute=extend_schema(request=inputs.DisputeInput, responses=StaffOrderSerializer),
    refunds=extend_schema(request=inputs.RefundInput, responses=StaffOrderSerializer),
    settlements=extend_schema(request=inputs.SettlementInput, responses=StaffOrderSerializer),
    cash_handover=extend_schema(request=inputs.EmptyInput, responses=StaffOrderSerializer),
    moderate_rating=extend_schema(request=inputs.ModerationInput, responses=StaffOrderSerializer),
)
class OrderViewSet(ParticipantOrderViewSet):
    permission_classes = (IsStaff,)

    def get_serializer_class(self):
        return StaffOrderSerializer

    def create(self, request):
        raise MethodNotAllowed("POST")

    def execute(self, service_name, input_class=inputs.EmptyInput, **extra):
        return super().execute(service_name, input_class, **extra)

    @action(detail=True, methods=["get"], url_path="eligible-plumbers")
    def eligible_plumbers(self, request, pk=None):
        order = self.get_object()
        queryset = selectors.eligible_plumbers(request.user, order.pk)
        return Response([
            {"user_id": user.pk, "name": user.get_full_name() or user.username,
             "profile_id": user.plumber_profile.pk, "phone_number": user.phone_number}
            for user in queryset.select_related("plumber_profile")
        ])

    @action(detail=True, methods=["get"], url_path="available-stores")
    def available_stores(self, request, pk=None):
        self.get_object()
        stores = Store.objects.filter(is_active=True, is_deleted=False, user__is_active=True, user__is_deleted=False).select_related("user").order_by("name", "pk")
        return Response(serializers.StoreSerializer(stores, many=True).data)

    @action(detail=True, methods=["post"], url_path="assign-plumber")
    def assign_plumber(self, request, pk=None):
        return self.execute("assign_plumber", inputs.AssignmentInput)

    @action(detail=True, methods=["post"], url_path="assign-store")
    def assign_store(self, request, pk=None):
        return self.execute("assign_store", inputs.StoreAssignmentInput)

    @action(detail=True, methods=["post"], url_path="confirm-urgent")
    def confirm_urgent(self, request, pk=None):
        return self.execute("confirm_urgent", inputs.UrgentInput)

    @action(detail=True, methods=["post"], url_path="sign-contract")
    def sign_contract(self, request, pk=None):
        return self.execute("sign_contract")

    @action(detail=True, methods=["post"], url_path="resolve-dispute")
    def resolve_dispute(self, request, pk=None):
        return self.execute("resolve_dispute", inputs.DisputeInput)

    @action(detail=True, methods=["post"], url_path="refunds")
    def refunds(self, request, pk=None):
        return self.execute("record_refund", inputs.RefundInput)

    @action(detail=True, methods=["post"], url_path="settlements")
    def settlements(self, request, pk=None):
        return self.execute("record_settlement", inputs.SettlementInput)

    @action(detail=True, methods=["post"], url_path=r"payments/(?P<payment_id>[0-9]+)/cash-handover")
    def cash_handover(self, request, pk=None, payment_id=None):
        return self.execute("confirm_cash_handover", payment_id=int(payment_id))

    @action(detail=True, methods=["post"], url_path=r"ratings/(?P<rating_id>[0-9]+)/moderate")
    def moderate_rating(self, request, pk=None, rating_id=None):
        return self.execute("moderate_rating", inputs.ModerationInput, rating_id=int(rating_id))


REPORT_COLUMNS = (
    "order_id", "status", "customer_id", "plumber_id", "store_id", "created_at",
    "total", "advance_required", "paid", "refunded", "net_paid", "balance_due",
    "plumber_rate", "store_rate", "plumber_commission", "store_commission",
    "plumber_net", "plumber_paid", "plumber_due", "store_net", "store_paid", "store_due",
)


def export_cell(value):
    if isinstance(value, str) and value.lstrip().startswith(("=", "+", "-", "@", "\t", "\r")):
        return "'" + value
    return value


class FinancialReportSerializer(drf_serializers.Serializer):
    currency = drf_serializers.CharField()
    count = drf_serializers.IntegerField()
    results = drf_serializers.ListField(child=drf_serializers.DictField())


class ReportView(APIView):
    permission_classes = (IsStaff,)
    serializer_class = FinancialReportSerializer

    def get(self, request):
        export = request.query_params.get("export", "json")
        if export not in {"json", "csv", "xlsx"}:
            raise ValidationError({"export": "Use json, csv or xlsx."})
        query = ReportFilter(data=request.query_params)
        query.is_valid(raise_exception=True)
        filters = query.validated_data
        queryset = selectors.orders_for(request.user)
        if filters.get("region"):
            queryset = queryset.filter(region_id=filters["region"])
        if filters.get("status"):
            queryset = queryset.filter(status=filters["status"])
        if filters.get("date_from"):
            queryset = queryset.filter(created_at__date__gte=filters["date_from"])
        if filters.get("date_to"):
            queryset = queryset.filter(created_at__date__lte=filters["date_to"])
        rows = []
        for order in queryset.iterator(chunk_size=200):
            row = {"order_id": order.pk, "status": order.status, "customer_id": order.customer_id,
                   "plumber_id": order.plumber_id, "store_id": order.store_id, "created_at": order.created_at.isoformat()}
            row.update(selectors.financial_summary(order))
            quote = order.quotes.filter(version=order.approved_version or order.quote_version).first()
            for key in ("plumber_rate", "store_rate", "plumber_commission", "store_commission"):
                row[key] = quote.snapshot.get(key, "0.00") if quote else "0.00"
            rows.append(monetary_projection(row))
        if export == "json":
            return Response({"currency": "UZS", "count": len(rows), "results": rows})
        if export == "csv":
            response = HttpResponse(content_type="text/csv; charset=utf-8")
            response.write("\ufeff")
            writer = csv.writer(response)
            writer.writerow(REPORT_COLUMNS)
            for row in rows:
                writer.writerow([export_cell(row.get(column)) for column in REPORT_COLUMNS])
        else:
            from openpyxl import Workbook

            workbook = Workbook(write_only=True)
            sheet = workbook.create_sheet("UZS")
            sheet.append(REPORT_COLUMNS)
            for row in rows:
                sheet.append([export_cell(row.get(column)) for column in REPORT_COLUMNS])
            buffer = BytesIO()
            workbook.save(buffer)
            response = HttpResponse(buffer.getvalue(), content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
        response["Content-Disposition"] = f'attachment; filename="santex-financial-report.{export}"'
        response["Cache-Control"] = "private, no-store"
        record(request.user, "api.report_export", request.user, {"format": export, "orders": len(rows)})
        return response


class ReportFilter(drf_serializers.Serializer):
    export = drf_serializers.ChoiceField(choices=["json", "csv", "xlsx"], required=False)
    region = drf_serializers.IntegerField(min_value=1, required=False)
    status = drf_serializers.ChoiceField(choices=models.Order.Status.choices, required=False)
    date_from = drf_serializers.DateField(required=False)
    date_to = drf_serializers.DateField(required=False)

    def validate(self, attrs):
        if attrs.get("date_from") and attrs.get("date_to") and attrs["date_from"] > attrs["date_to"]:
            raise ValidationError({"date_to": "Must be on or after date_from."})
        return attrs
