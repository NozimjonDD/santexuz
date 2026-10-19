import uuid

from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from project_backend.base_model import BaseModel


class Order(BaseModel):
    class Status(models.TextChoices):
        REQUESTED = "requested", "So‘rov yuborildi"
        ASSIGNED = "assigned", "Santexnik biriktirildi"
        ACCEPTED = "accepted", "Santexnik qabul qildi"
        INSPECTION = "inspection", "Ko‘rik belgilandi"
        ESTIMATE = "estimate", "Materiallar ro‘yxati tayyor"
        STORE_ASSIGNED = "store_assigned", "Do‘kon biriktirildi"
        STORE_ACCEPTED = "store_accepted", "Do‘kon qabul qildi"
        QUOTED = "quoted", "Smeta tayyor"
        APPROVED = "approved", "Smeta tasdiqlandi"
        PREPARING = "preparing", "Tayyorlanmoqda"
        DELIVERING = "delivering", "Yo‘lda"
        DELIVERED = "delivered", "Materiallar qabul qilindi"
        WORKING = "working", "Ish boshlandi"
        COMPLETED = "completed", "Usta yakunladi"
        CUSTOMER_ACCEPTED = "customer_accepted", "Mijoz tasdiqladi"
        DISPUTED = "disputed", "Nizo"
        REJECTED = "rejected", "Smeta rad etildi"
        CANCELLED = "cancelled", "Bekor qilindi"
        CLOSED = "closed", "Yopildi"

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="customer_orders")
    plumber = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="plumber_orders", null=True, blank=True)
    store = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="store_orders", null=True, blank=True)
    region = models.ForeignKey("catalog.Region", on_delete=models.PROTECT)
    service_group = models.ForeignKey("catalog.ServiceGroup", on_delete=models.PROTECT)
    status = models.CharField(max_length=32, choices=Status.choices, default=Status.REQUESTED, db_index=True)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    description = models.TextField(blank=True)
    consent_at = models.DateTimeField()
    phone_snapshot = models.CharField(max_length=32)
    is_urgent = models.BooleanField(default=False)
    urgent_confirmed = models.BooleanField(default=False)
    plumber_accepted = models.BooleanField(default=False)
    store_accepted = models.BooleanField(default=False)
    response_due_at = models.DateTimeField(null=True, blank=True)
    response_alerted_at = models.DateTimeField(null=True, blank=True)
    inspection_at = models.DateTimeField(null=True, blank=True)
    work_starts_at = models.DateTimeField(null=True, blank=True)
    work_ends_at = models.DateTimeField(null=True, blank=True)
    preparation_started_at = models.DateTimeField(null=True, blank=True)
    work_started_at = models.DateTimeField(null=True, blank=True)
    customer_accepted_at = models.DateTimeField(null=True, blank=True)
    quote_version = models.PositiveIntegerField(default=0)
    approved_version = models.PositiveIntegerField(null=True, blank=True)
    delivery_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    preparation_minutes = models.PositiveIntegerField(default=0)
    refund_limit = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    company_failure = models.BooleanField(default=False)
    rejected_plumber_ids = models.JSONField(default=list, blank=True)

    class Meta:
        db_table = "orders_order"
        ordering = ["-created_at", "-pk"]
        constraints = [
            models.CheckConstraint(condition=models.Q(latitude__gte=-90, latitude__lte=90, longitude__gte=-180, longitude__lte=180), name="orders_location_range"),
            models.CheckConstraint(condition=models.Q(delivery_fee__gte=0, refund_limit__gte=0), name="orders_nonnegative_money"),
        ]


class ServiceItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="service_items")
    service = models.ForeignKey("catalog.Service", on_delete=models.PROTECT)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=32)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=16, decimal_places=2)
    urgent_fee = models.DecimalField(max_digits=16, decimal_places=2, default=0)
    warranty_days = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "orders_serviceitem"
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0, unit_price__gte=0, urgent_fee__gte=0), name="orders_service_item_values")]


class MaterialItem(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="material_items")
    material = models.ForeignKey("catalog.Material", on_delete=models.PROTECT, null=True, blank=True)
    name = models.CharField(max_length=255)
    unit = models.CharField(max_length=32)
    brand = models.CharField(max_length=150, blank=True)
    note = models.TextField(blank=True)
    quantity = models.DecimalField(max_digits=12, decimal_places=3)
    unit_price = models.DecimalField(max_digits=16, decimal_places=2, null=True, blank=True)
    available = models.BooleanField(default=False)
    replacement_name = models.CharField(max_length=255, blank=True)
    supply_minutes = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = "orders_materialitem"
        constraints = [models.CheckConstraint(condition=models.Q(quantity__gt=0) & (models.Q(unit_price__isnull=True) | models.Q(unit_price__gte=0)), name="orders_material_item_values")]


class ImmutableQuerySet(models.QuerySet):
    def update(self, **kwargs):
        raise ValueError("Immutable records cannot be updated.")

    def delete(self):
        raise ValueError("Immutable records cannot be deleted.")


class ImmutableRecord(BaseModel):
    objects = ImmutableQuerySet.as_manager()

    def save(self, *args, **kwargs):
        if self.pk:
            raise ValueError("Immutable records cannot be changed.")
        return super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        raise ValueError("Immutable records cannot be deleted.")

    class Meta:
        abstract = True


class Quote(ImmutableRecord):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="quotes")
    version = models.PositiveIntegerField()
    snapshot = models.JSONField()
    total = models.DecimalField(max_digits=16, decimal_places=2)
    advance_required = models.DecimalField(max_digits=16, decimal_places=2)

    class Meta:
        db_table = "orders_quote"
        constraints = [models.UniqueConstraint(fields=["order", "version"], name="orders_quote_version_unique"),
                       models.CheckConstraint(condition=models.Q(total__gt=0, advance_required__gte=0, advance_required__lte=models.F("total")), name="orders_quote_values")]
        ordering = ["-version"]


class Contract(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="contracts")
    quote = models.OneToOneField(Quote, on_delete=models.PROTECT, related_name="contract")
    language = models.CharField(max_length=2)
    template_version = models.PositiveIntegerField()
    text_snapshot = models.TextField()
    parties_snapshot = models.JSONField(default=dict)
    signed_at = models.DateTimeField(null=True, blank=True)
    signed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = "orders_contract"

    def save(self, *args, **kwargs):
        if self.pk:
            original = type(self).objects.get(pk=self.pk)
            fields = ["quote_id", "order_id", "language", "template_version", "text_snapshot", "parties_snapshot"]
            if original.signed_at or any(getattr(self, key) != getattr(original, key) for key in fields):
                raise ValueError("Contract snapshot is immutable.")
        return super().save(*args, **kwargs)


class Delivery(BaseModel):
    class Status(models.TextChoices):
        PREPARING = "preparing", "Tayyorlanmoqda"
        DISPATCHED = "dispatched", "Yo‘lda"
        DELIVERED = "delivered", "Yetkazildi"
        CONFIRMED = "confirmed", "Mijoz qabul qildi"

    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="deliveries")
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.PREPARING)
    eta = models.DateTimeField(null=True, blank=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "orders_delivery"


class DeliveryItem(BaseModel):
    delivery = models.ForeignKey(Delivery, on_delete=models.CASCADE, related_name="items")
    item = models.ForeignKey(MaterialItem, on_delete=models.PROTECT, related_name="delivery_items")
    quantity = models.DecimalField(max_digits=12, decimal_places=3)

    class Meta:
        db_table = "orders_deliveryitem"
        constraints = [models.UniqueConstraint(fields=["delivery", "item"], name="orders_delivery_item_unique"),
                       models.CheckConstraint(condition=models.Q(quantity__gt=0), name="orders_delivery_quantity_positive")]


class Payment(ImmutableRecord):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="payments")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    method = models.CharField(max_length=16, choices=[("cash", "Naqd"), ("terminal", "Terminal")])
    kind = models.CharField(max_length=16, choices=[("advance", "Avans"), ("balance", "Qoldiq")])
    received_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "orders_payment"
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name="orders_payment_positive")]


class Refund(ImmutableRecord):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="refunds")
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    reason = models.TextField()
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "orders_refund"
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name="orders_refund_positive")]


class CashHandover(ImmutableRecord):
    payment = models.OneToOneField(Payment, on_delete=models.PROTECT, related_name="handover")
    confirmed_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)

    class Meta:
        db_table = "orders_cashhandover"


class Settlement(ImmutableRecord):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="settlements")
    partner = models.CharField(max_length=16, choices=[("plumber", "Santexnik"), ("store", "Do‘kon")])
    amount = models.DecimalField(max_digits=16, decimal_places=2)
    recorded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    idempotency_key = models.CharField(max_length=128, unique=True)

    class Meta:
        db_table = "orders_settlement"
        constraints = [models.CheckConstraint(condition=models.Q(amount__gt=0), name="orders_settlement_positive")]


class Issue(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="issues")
    opened_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="opened_order_issues")
    description = models.TextField()
    resolution = models.TextField(blank=True)
    resolved_at = models.DateTimeField(null=True, blank=True)
    resolved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True, related_name="resolved_order_issues")
    previous_status = models.CharField(max_length=32)

    class Meta:
        db_table = "orders_issue"


class Rating(BaseModel):
    order = models.OneToOneField(Order, on_delete=models.PROTECT, related_name="rating")
    plumber_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    store_score = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    approved = models.BooleanField(default=False)
    moderated_at = models.DateTimeField(null=True, blank=True)
    moderated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True, blank=True)

    class Meta:
        db_table = "orders_rating"
        constraints = [models.CheckConstraint(condition=models.Q(plumber_score__gte=1, plumber_score__lte=5, store_score__gte=1, store_score__lte=5), name="orders_rating_range")]


def protected_upload(instance, filename):
    suffix = filename.rsplit(".", 1)[-1].lower()
    return f"orders/{instance.order_id}/{uuid.uuid4().hex}.{suffix}"


class Attachment(BaseModel):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="attachments")
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    file = models.FileField(upload_to=protected_upload)
    purpose = models.CharField(max_length=16, choices=[("request", "So‘rov"), ("issue", "Muammo"), ("completion", "Natija")])

    class Meta:
        db_table = "orders_attachment"


class OrderEvent(ImmutableRecord):
    order = models.ForeignKey(Order, on_delete=models.PROTECT, related_name="events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, null=True)
    action = models.CharField(max_length=64)
    status = models.CharField(max_length=32)
    payload = models.JSONField(default=dict)

    class Meta:
        db_table = "orders_orderevent"
        ordering = ["created_at", "pk"]
