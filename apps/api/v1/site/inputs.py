"""Strict request contracts; pricing and permissions remain in domain services."""

from decimal import Decimal

from rest_framework import serializers


class StrictSerializer(serializers.Serializer):
    def to_internal_value(self, data):
        if not isinstance(data, dict):
            raise serializers.ValidationError("JSON object expected.")
        unknown = set(data) - set(self.fields)
        if unknown:
            raise serializers.ValidationError({key: "Unknown field." for key in unknown})
        return super().to_internal_value(data)


class EmptyInput(StrictSerializer):
    pass


class OrderCreateInput(StrictSerializer):
    region_id = serializers.IntegerField(min_value=1)
    service_group_id = serializers.IntegerField(min_value=1)
    address = serializers.CharField(max_length=500)
    latitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=-90, max_value=90)
    longitude = serializers.DecimalField(max_digits=9, decimal_places=6, min_value=-180, max_value=180)
    consent = serializers.BooleanField()
    is_urgent = serializers.BooleanField(default=False)
    description = serializers.CharField(max_length=5000, required=False, allow_blank=True, default="")

    def validate_consent(self, value):
        if not value:
            raise serializers.ValidationError("Personal data sharing consent is required.")
        return value


class ResponseInput(StrictSerializer):
    accept = serializers.BooleanField()
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if not attrs["accept"] and not attrs["reason"].strip():
            raise serializers.ValidationError({"reason": "Explain why the request is declined."})
        return attrs


class InspectionInput(StrictSerializer):
    inspection_at = serializers.DateTimeField()


class ServiceLineInput(StrictSerializer):
    service_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=Decimal("0.001"))


class MaterialLineInput(StrictSerializer):
    material_id = serializers.IntegerField(min_value=1, required=False, allow_null=True)
    name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    unit = serializers.CharField(max_length=32, required=False, allow_blank=True)
    brand = serializers.CharField(max_length=120, required=False, allow_blank=True, default="")
    note = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=Decimal("0.001"))

    def validate(self, attrs):
        if not attrs.get("material_id") and (not attrs.get("name") or not attrs.get("unit")):
            raise serializers.ValidationError("Free-form materials require name and unit.")
        return attrs


class EstimateInput(StrictSerializer):
    services = ServiceLineInput(many=True, allow_empty=False, max_length=200)
    materials = MaterialLineInput(many=True, max_length=500)

    def validate_services(self, value):
        ids = [item["service_id"] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Duplicate services are not allowed.")
        return value


class MaterialPriceInput(StrictSerializer):
    id = serializers.IntegerField(min_value=1)
    unit_price = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal("0"))
    available = serializers.BooleanField()
    replacement_name = serializers.CharField(max_length=255, required=False, allow_blank=True, default="")
    supply_minutes = serializers.IntegerField(min_value=0, max_value=525600, default=0)


class PriceMaterialsInput(StrictSerializer):
    items = MaterialPriceInput(many=True, max_length=500)
    delivery_fee = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal("0"))
    preparation_minutes = serializers.IntegerField(min_value=0, max_value=525600)

    def validate_items(self, value):
        ids = [item["id"] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Duplicate material lines are not allowed.")
        return value


class ReasonInput(StrictSerializer):
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")


class QuoteApprovalInput(StrictSerializer):
    quote_version = serializers.IntegerField(min_value=1)


class QuoteRejectionInput(ReasonInput):
    quote_version = serializers.IntegerField(min_value=1)


class PaymentInput(StrictSerializer):
    amount = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal("0.01"))
    method = serializers.ChoiceField(choices=["cash", "terminal"])
    kind = serializers.ChoiceField(choices=["advance", "balance"])
    idempotency_key = serializers.CharField(max_length=128)


class DeliveryItemInput(StrictSerializer):
    item_id = serializers.IntegerField(min_value=1)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=3, min_value=Decimal("0.001"))


class DeliveryCreateInput(StrictSerializer):
    items = DeliveryItemInput(many=True, allow_empty=False, max_length=500)
    eta = serializers.DateTimeField(required=False, allow_null=True, default=None)

    def validate_items(self, value):
        ids = [item["item_id"] for item in value]
        if len(ids) != len(set(ids)):
            raise serializers.ValidationError("Duplicate delivery lines are not allowed.")
        return value


class DeliveryUpdateInput(StrictSerializer):
    status = serializers.ChoiceField(choices=["preparing", "dispatched", "delivered"])
    eta = serializers.DateTimeField(required=False, allow_null=True, default=None)


class IssueInput(StrictSerializer):
    description = serializers.CharField(max_length=5000)


class WorkScheduleInput(StrictSerializer):
    starts_at = serializers.DateTimeField()
    ends_at = serializers.DateTimeField()
    reason = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")

    def validate(self, attrs):
        if attrs["ends_at"] <= attrs["starts_at"]:
            raise serializers.ValidationError({"ends_at": "Must be later than starts_at."})
        return attrs


class RatingInput(StrictSerializer):
    plumber_score = serializers.IntegerField(min_value=1, max_value=5)
    store_score = serializers.IntegerField(min_value=1, max_value=5)
    comment = serializers.CharField(max_length=2000, required=False, allow_blank=True, default="")


class AssignmentInput(StrictSerializer):
    plumber_id = serializers.IntegerField(min_value=1)


class StoreAssignmentInput(StrictSerializer):
    store_id = serializers.IntegerField(min_value=1)


class UrgentInput(StrictSerializer):
    confirmed = serializers.BooleanField()


class DisputeInput(StrictSerializer):
    note = serializers.CharField(max_length=5000)
    accept_work = serializers.BooleanField(default=True)


class CancelInput(ReasonInput):
    company_failure = serializers.BooleanField(default=False)


class RefundInput(StrictSerializer):
    amount = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal("0.01"))
    reason = serializers.CharField(max_length=2000)
    idempotency_key = serializers.CharField(max_length=128)


class SettlementInput(StrictSerializer):
    partner = serializers.ChoiceField(choices=["plumber", "store"])
    amount = serializers.DecimalField(max_digits=16, decimal_places=2, min_value=Decimal("0.01"))
    idempotency_key = serializers.CharField(max_length=128)


class ModerationInput(StrictSerializer):
    approved = serializers.BooleanField()
