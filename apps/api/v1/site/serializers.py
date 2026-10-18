"""Participant-safe projections. Internal commission data is staff-only."""

from rest_framework import serializers
from decimal import Decimal

from apps.api.common.serializers import PublicPlumberSerializer, PublicStoreSerializer
from apps.orders import models


def monetary_projection(values):
    return {key: format(value, ".2f") if isinstance(value, Decimal) else value for key, value in values.items()}


class ServiceItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.ServiceItem
        fields = ("id", "service", "name", "unit", "quantity", "unit_price", "urgent_fee", "warranty_days")


class MaterialItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.MaterialItem
        fields = ("id", "material", "name", "unit", "brand", "note", "quantity", "unit_price", "available", "replacement_name", "supply_minutes")


class QuoteSerializer(serializers.ModelSerializer):
    snapshot = serializers.SerializerMethodField()

    def get_snapshot(self, obj) -> dict:
        # A snapshot can contain accounting metadata. Only customer invoice fields
        # are included here, even when future services add internal snapshot keys.
        visible = {
            "currency", "vat_included", "services", "materials", "service_items", "material_items",
            "services_total", "service_total", "materials_total", "material_total",
            "delivery_fee", "urgent_fee", "urgent_total", "platform_fee", "total",
            "advance_required", "preparation_minutes", "travel_minutes", "estimated_delivery_minutes", "work_starts_at", "work_ends_at",
        }
        return {key: value for key, value in obj.snapshot.items() if key in visible}

    class Meta:
        model = models.Quote
        fields = ("id", "version", "snapshot", "total", "advance_required", "created_at")


class ContractSerializer(serializers.ModelSerializer):
    quote_version = serializers.IntegerField(source="quote.version", read_only=True)

    class Meta:
        model = models.Contract
        fields = ("id", "quote", "quote_version", "language", "template_version", "text_snapshot", "signed_at", "created_at")


class PaymentSerializer(serializers.ModelSerializer):
    received_by_name = serializers.SerializerMethodField()
    fiscal_receipt = serializers.SerializerMethodField()

    def get_received_by_name(self, obj) -> str:
        return obj.received_by.get_full_name() or obj.received_by.username

    def get_fiscal_receipt(self, obj) -> bool:
        return False

    class Meta:
        model = models.Payment
        fields = ("id", "amount", "method", "kind", "received_by", "received_by_name", "created_at", "fiscal_receipt")


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Refund
        fields = ("id", "amount", "reason", "created_at")


class DeliveryItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.DeliveryItem
        fields = ("id", "item", "quantity")


class DeliverySerializer(serializers.ModelSerializer):
    items = DeliveryItemSerializer(many=True, read_only=True)

    class Meta:
        model = models.Delivery
        fields = ("id", "status", "eta", "confirmed_at", "items", "created_at", "updated_at")


class IssueSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Issue
        fields = ("id", "description", "resolution", "resolved_at", "created_at")


class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Rating
        fields = ("id", "plumber_score", "store_score", "comment", "approved", "created_at")


class AttachmentSerializer(serializers.ModelSerializer):
    download_path = serializers.SerializerMethodField()

    def get_download_path(self, obj) -> str:
        return f"/api/v1/site/orders/{obj.order_id}/attachments/{obj.pk}/download/"

    class Meta:
        model = models.Attachment
        fields = ("id", "purpose", "download_path", "created_at")


class OrderEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.OrderEvent
        # Actor identifiers and arbitrary payloads belong to the staff audit log.
        fields = ("id", "action", "status", "created_at")


class OrderListSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Order
        fields = (
            "id", "status", "region", "service_group", "address", "is_urgent", "urgent_confirmed",
            "inspection_at", "work_starts_at", "work_ends_at", "quote_version", "approved_version",
            "created_at", "updated_at",
        )


class OrderSerializer(OrderListSerializer):
    plumber = serializers.SerializerMethodField()
    store = serializers.SerializerMethodField()
    customer = serializers.SerializerMethodField()
    service_items = ServiceItemSerializer(many=True, read_only=True)
    material_items = MaterialItemSerializer(many=True, read_only=True)
    quotes = QuoteSerializer(many=True, read_only=True)
    contracts = ContractSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    refunds = RefundSerializer(many=True, read_only=True)
    deliveries = DeliverySerializer(many=True, read_only=True)
    issues = IssueSerializer(many=True, read_only=True)
    rating = RatingSerializer(read_only=True)
    attachments = AttachmentSerializer(many=True, read_only=True)
    events = OrderEventSerializer(many=True, read_only=True)
    accounting = serializers.SerializerMethodField()

    def get_customer(self, obj) -> dict:
        return {"id": obj.customer_id, "name": obj.customer.get_full_name() or obj.customer.username, "phone_number": obj.phone_snapshot}

    def get_accounting(self, obj) -> dict:
        from apps.orders.selectors import financial_summary

        summary = financial_summary(obj)
        actor = self.context["request"].user
        if actor.is_staff:
            return monetary_projection(summary)
        if actor.pk == obj.customer_id:
            return monetary_projection({key: summary[key] for key in ("paid", "refunded", "net_paid", "total", "advance_required", "balance_due")})
        partner = "plumber" if actor.pk == obj.plumber_id else "store"
        return monetary_projection({"settlement_paid": summary[f"{partner}_paid"]})

    def get_plumber(self, obj) -> dict | None:
        if not obj.plumber_id or (not obj.plumber_accepted and not self.context["request"].user.is_staff):
            return None
        profile = getattr(obj.plumber, "plumber_profile", None)
        if profile is None:
            return None
        data = dict(PublicPlumberSerializer(profile, context=self.context).data)
        data["user_id"] = obj.plumber_id
        actor = self.context["request"].user
        if actor.is_staff or actor.pk == obj.customer_id:
            data["phone_number"] = obj.plumber.phone_number
        return data

    def get_store(self, obj) -> dict | None:
        profile = getattr(obj.store, "store_profile", None) if obj.store_id else None
        return PublicStoreSerializer(profile, context=self.context).data if profile else None

    class Meta(OrderListSerializer.Meta):
        fields = OrderListSerializer.Meta.fields + (
            "latitude", "longitude", "description", "consent_at", "customer", "plumber", "store",
            "plumber_accepted", "store_accepted", "response_due_at", "preparation_minutes",
            "preparation_started_at", "work_started_at", "customer_accepted_at", "delivery_fee",
            "service_items", "material_items", "quotes", "contracts", "payments", "refunds",
            "deliveries", "issues", "rating", "attachments", "events", "accounting",
        )


class AttachmentInput(serializers.Serializer):
    file = serializers.FileField()
    purpose = serializers.ChoiceField(choices=["request", "issue", "completion"])

    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("Form object expected.")
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: "Unknown field." for key in unknown})
        return super().to_internal_value(data)
