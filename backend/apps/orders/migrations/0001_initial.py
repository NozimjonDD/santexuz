"""Hand-authored from docs/orders_schema.sql; run only on the deployment machine."""
import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
import apps.orders.models


def identity():
    return ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"))


def timestamps():
    return [("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True))]


def created():
    return [("created_at", models.DateTimeField(auto_now_add=True))]


def fk(target, **kwargs):
    return models.ForeignKey(to=target, on_delete=django.db.models.deletion.PROTECT, **kwargs)


def amount(**kwargs):
    return models.DecimalField(max_digits=16, decimal_places=2, **kwargs)


STATUS_CHOICES = [
    ("requested", "So‘rov yuborildi"), ("assigned", "Santexnik biriktirildi"),
    ("accepted", "Santexnik qabul qildi"), ("inspection", "Ko‘rik belgilandi"),
    ("estimate", "Materiallar ro‘yxati tayyor"), ("store_assigned", "Do‘kon biriktirildi"),
    ("store_accepted", "Do‘kon qabul qildi"), ("quoted", "Smeta tayyor"),
    ("approved", "Smeta tasdiqlandi"), ("preparing", "Tayyorlanmoqda"),
    ("delivering", "Yo‘lda"), ("delivered", "Materiallar qabul qilindi"),
    ("working", "Ish boshlandi"), ("completed", "Usta yakunladi"),
    ("customer_accepted", "Mijoz tasdiqladi"), ("disputed", "Nizo"),
    ("rejected", "Smeta rad etildi"), ("cancelled", "Bekor qilindi"), ("closed", "Yopildi"),
]


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("catalog", "0001_initial")]
    operations = [
        migrations.CreateModel(name="Order", fields=[identity(), *timestamps(),
            ("customer", fk(settings.AUTH_USER_MODEL, related_name="customer_orders")),
            ("plumber", fk(settings.AUTH_USER_MODEL, related_name="plumber_orders", null=True, blank=True)),
            ("store", fk(settings.AUTH_USER_MODEL, related_name="store_orders", null=True, blank=True)),
            ("region", fk("catalog.region")), ("service_group", fk("catalog.servicegroup")),
            ("status", models.CharField(max_length=32, choices=STATUS_CHOICES, default="requested", db_index=True)),
            ("address", models.TextField()), ("latitude", models.DecimalField(max_digits=9, decimal_places=6)),
            ("longitude", models.DecimalField(max_digits=9, decimal_places=6)), ("description", models.TextField(blank=True)),
            ("consent_at", models.DateTimeField()), ("phone_snapshot", models.CharField(max_length=32)),
            ("is_urgent", models.BooleanField(default=False)), ("urgent_confirmed", models.BooleanField(default=False)),
            ("plumber_accepted", models.BooleanField(default=False)), ("store_accepted", models.BooleanField(default=False)),
            ("response_due_at", models.DateTimeField(null=True, blank=True)),
            ("response_alerted_at", models.DateTimeField(null=True, blank=True)),
            ("inspection_at", models.DateTimeField(null=True, blank=True)),
            ("work_starts_at", models.DateTimeField(null=True, blank=True)),
            ("work_ends_at", models.DateTimeField(null=True, blank=True)),
            ("preparation_started_at", models.DateTimeField(null=True, blank=True)),
            ("work_started_at", models.DateTimeField(null=True, blank=True)),
            ("customer_accepted_at", models.DateTimeField(null=True, blank=True)),
            ("quote_version", models.PositiveIntegerField(default=0)),
            ("approved_version", models.PositiveIntegerField(null=True, blank=True)),
            ("delivery_fee", amount(default=0)), ("preparation_minutes", models.PositiveIntegerField(default=0)),
            ("refund_limit", amount(default=0)), ("company_failure", models.BooleanField(default=False)),
            ("rejected_plumber_ids", models.JSONField(default=list, blank=True)),
        ], options={"ordering": ["-created_at", "-pk"], "constraints": [
            models.CheckConstraint(condition=models.Q(latitude__gte=-90, latitude__lte=90, longitude__gte=-180, longitude__lte=180), name="orders_location_range"),
            models.CheckConstraint(condition=models.Q(delivery_fee__gte=0, refund_limit__gte=0), name="orders_nonnegative_money")]}),
        migrations.CreateModel(name="ServiceItem", fields=[identity(), *timestamps(),
            ("order", models.ForeignKey(to="orders.order", on_delete=django.db.models.deletion.CASCADE, related_name="service_items")),
            ("service", fk("catalog.service")), ("name", models.CharField(max_length=255)),
            ("unit", models.CharField(max_length=32)), ("quantity", models.DecimalField(max_digits=12, decimal_places=3)),
            ("unit_price", amount()), ("urgent_fee", amount(default=0)), ("warranty_days", models.PositiveIntegerField(default=0)),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(quantity__gt=0, unit_price__gte=0, urgent_fee__gte=0), name="orders_service_item_values")]}),
        migrations.CreateModel(name="MaterialItem", fields=[identity(), *timestamps(),
            ("order", models.ForeignKey(to="orders.order", on_delete=django.db.models.deletion.CASCADE, related_name="material_items")),
            ("material", fk("catalog.material", null=True, blank=True)), ("name", models.CharField(max_length=255)),
            ("unit", models.CharField(max_length=32)), ("brand", models.CharField(max_length=150, blank=True)),
            ("note", models.TextField(blank=True)), ("quantity", models.DecimalField(max_digits=12, decimal_places=3)),
            ("unit_price", amount(null=True, blank=True)), ("available", models.BooleanField(default=False)),
            ("replacement_name", models.CharField(max_length=255, blank=True)), ("supply_minutes", models.PositiveIntegerField(default=0)),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(quantity__gt=0) & (models.Q(unit_price__isnull=True) | models.Q(unit_price__gte=0)), name="orders_material_item_values")]}),
        migrations.CreateModel(name="Quote", fields=[identity(), *created(),
            ("order", fk("orders.order", related_name="quotes")), ("version", models.PositiveIntegerField()),
            ("snapshot", models.JSONField()), ("total", amount()), ("advance_required", amount()),
        ], options={"ordering": ["-version"], "constraints": [
            models.UniqueConstraint(fields=["order", "version"], name="orders_quote_version_unique"),
            models.CheckConstraint(condition=models.Q(total__gt=0, advance_required__gte=0, advance_required__lte=models.F("total")), name="orders_quote_values")]}),
        migrations.CreateModel(name="Contract", fields=[identity(), *timestamps(),
            ("order", fk("orders.order", related_name="contracts")),
            ("quote", models.OneToOneField(to="orders.quote", on_delete=django.db.models.deletion.PROTECT, related_name="contract")),
            ("language", models.CharField(max_length=2)), ("template_version", models.PositiveIntegerField()),
            ("text_snapshot", models.TextField()), ("parties_snapshot", models.JSONField(default=dict)),
            ("signed_at", models.DateTimeField(null=True, blank=True)),
            ("signed_by", fk(settings.AUTH_USER_MODEL, null=True, blank=True)),
        ]),
        migrations.CreateModel(name="Delivery", fields=[identity(), *timestamps(),
            ("order", fk("orders.order", related_name="deliveries")),
            ("status", models.CharField(max_length=16, choices=[("preparing", "Tayyorlanmoqda"), ("dispatched", "Yo‘lda"), ("delivered", "Yetkazildi"), ("confirmed", "Mijoz qabul qildi")], default="preparing")),
            ("eta", models.DateTimeField(null=True, blank=True)), ("confirmed_at", models.DateTimeField(null=True, blank=True)),
        ]),
        migrations.CreateModel(name="DeliveryItem", fields=[identity(),
            ("delivery", models.ForeignKey(to="orders.delivery", on_delete=django.db.models.deletion.CASCADE, related_name="items")),
            ("item", fk("orders.materialitem", related_name="delivery_items")), ("quantity", models.DecimalField(max_digits=12, decimal_places=3)),
        ], options={"constraints": [models.UniqueConstraint(fields=["delivery", "item"], name="orders_delivery_item_unique"),
                                  models.CheckConstraint(condition=models.Q(quantity__gt=0), name="orders_delivery_quantity_positive")]}),
        migrations.CreateModel(name="Payment", fields=[identity(), *created(),
            ("order", fk("orders.order", related_name="payments")), ("amount", amount()),
            ("method", models.CharField(max_length=16, choices=[("cash", "Naqd"), ("terminal", "Terminal")])),
            ("kind", models.CharField(max_length=16, choices=[("advance", "Avans"), ("balance", "Qoldiq")])),
            ("received_by", fk(settings.AUTH_USER_MODEL)), ("idempotency_key", models.CharField(max_length=128, unique=True)),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(amount__gt=0), name="orders_payment_positive")]}),
        migrations.CreateModel(name="Refund", fields=[identity(), *created(),
            ("order", fk("orders.order", related_name="refunds")), ("amount", amount()), ("reason", models.TextField()),
            ("recorded_by", fk(settings.AUTH_USER_MODEL)), ("idempotency_key", models.CharField(max_length=128, unique=True)),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(amount__gt=0), name="orders_refund_positive")]}),
        migrations.CreateModel(name="CashHandover", fields=[identity(), *created(),
            ("payment", models.OneToOneField(to="orders.payment", on_delete=django.db.models.deletion.PROTECT, related_name="handover")),
            ("confirmed_by", fk(settings.AUTH_USER_MODEL)),
        ]),
        migrations.CreateModel(name="Settlement", fields=[identity(), *created(),
            ("order", fk("orders.order", related_name="settlements")),
            ("partner", models.CharField(max_length=16, choices=[("plumber", "Santexnik"), ("store", "Do‘kon")])),
            ("amount", amount()), ("recorded_by", fk(settings.AUTH_USER_MODEL)),
            ("idempotency_key", models.CharField(max_length=128, unique=True)),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(amount__gt=0), name="orders_settlement_positive")]}),
        migrations.CreateModel(name="Issue", fields=[identity(), *timestamps(),
            ("order", fk("orders.order", related_name="issues")),
            ("opened_by", fk(settings.AUTH_USER_MODEL, related_name="opened_order_issues")),
            ("description", models.TextField()), ("resolution", models.TextField(blank=True)),
            ("resolved_at", models.DateTimeField(null=True, blank=True)),
            ("resolved_by", fk(settings.AUTH_USER_MODEL, null=True, blank=True, related_name="resolved_order_issues")),
            ("previous_status", models.CharField(max_length=32)),
        ]),
        migrations.CreateModel(name="Rating", fields=[identity(), *timestamps(),
            ("order", models.OneToOneField(to="orders.order", on_delete=django.db.models.deletion.PROTECT, related_name="rating")),
            ("plumber_score", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ("store_score", models.PositiveSmallIntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
            ("comment", models.TextField(blank=True)), ("approved", models.BooleanField(default=False)),
            ("moderated_at", models.DateTimeField(null=True, blank=True)),
            ("moderated_by", fk(settings.AUTH_USER_MODEL, null=True, blank=True)),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(plumber_score__gte=1, plumber_score__lte=5, store_score__gte=1, store_score__lte=5), name="orders_rating_range")]}),
        migrations.CreateModel(name="Attachment", fields=[identity(), *timestamps(),
            ("order", fk("orders.order", related_name="attachments")), ("uploaded_by", fk(settings.AUTH_USER_MODEL)),
            ("file", models.FileField(upload_to=apps.orders.models.protected_upload)),
            ("purpose", models.CharField(max_length=16, choices=[("request", "So‘rov"), ("issue", "Muammo"), ("completion", "Natija")])),
        ]),
        migrations.CreateModel(name="OrderEvent", fields=[identity(), *created(),
            ("order", fk("orders.order", related_name="events")), ("actor", fk(settings.AUTH_USER_MODEL, null=True)),
            ("action", models.CharField(max_length=64)), ("status", models.CharField(max_length=32)), ("payload", models.JSONField(default=dict)),
        ], options={"ordering": ["created_at", "pk"]}),
    ]
