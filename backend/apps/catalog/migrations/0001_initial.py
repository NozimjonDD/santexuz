import django.core.validators
import django.db.models.deletion
from django.db import migrations, models

import apps.catalog.models


def timestamps():
    return [("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True))]


def identity():
    return [("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"))]


class Migration(migrations.Migration):
    initial = True
    dependencies = []
    operations = [
        migrations.CreateModel(name="Region", fields=identity() + timestamps() + [
            ("name", models.CharField(max_length=150)),
            ("code", models.SlugField(max_length=50, unique=True)),
            ("is_active", models.BooleanField(default=True)),
        ], options={"ordering": ("name", "id")}),
        migrations.CreateModel(name="ServiceGroup", fields=identity() + timestamps() + [
            ("name", models.CharField(max_length=150)),
            ("name_ru", models.CharField(blank=True, max_length=150)),
            ("name_en", models.CharField(blank=True, max_length=150)),
            ("code", models.SlugField(max_length=50, unique=True)),
            ("is_active", models.BooleanField(default=True)),
        ], options={"ordering": ("name", "id")}),
        migrations.CreateModel(name="Material", fields=identity() + timestamps() + [
            ("name", models.CharField(max_length=200)),
            ("unit", models.CharField(max_length=30)),
            ("brand", models.CharField(blank=True, max_length=150)),
            ("is_active", models.BooleanField(default=True)),
        ], options={"ordering": ("name", "id")}),
        migrations.CreateModel(name="Service", fields=identity() + timestamps() + [
            ("name", models.CharField(max_length=200)),
            ("name_ru", models.CharField(blank=True, max_length=200)),
            ("name_en", models.CharField(blank=True, max_length=200)),
            ("unit", models.CharField(max_length=30)),
            ("warranty_days", models.PositiveIntegerField(default=0)),
            ("is_active", models.BooleanField(default=True)),
            ("group", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="services", to="catalog.servicegroup")),
        ], options={"ordering": ("name", "id")}),
        migrations.CreateModel(name="ServiceRate", fields=identity() + timestamps() + [
            ("unit_price", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
            ("urgent_fee", models.DecimalField(decimal_places=2, default=0, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
            ("region", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rates", to="catalog.region")),
            ("service", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="rates", to="catalog.service")),
        ], options={"constraints": [
            models.UniqueConstraint(fields=("region", "service"), name="unique_region_service_rate"),
            models.CheckConstraint(condition=models.Q(unit_price__gte=0, urgent_fee__gte=0), name="nonnegative_service_rate"),
        ]}),
        migrations.CreateModel(name="ServiceCenter", fields=identity() + timestamps() + [
            ("name", models.CharField(max_length=200)),
            ("address", models.TextField()), ("phone", models.CharField(max_length=20)),
            ("opening_time", models.TimeField()), ("closing_time", models.TimeField()),
            ("working_days", models.JSONField(validators=[apps.catalog.models.validate_working_days])),
            ("default_plumber_commission", models.DecimalField(decimal_places=2, max_digits=5, validators=apps.catalog.models.PERCENT_VALIDATORS)),
            ("default_store_commission", models.DecimalField(decimal_places=2, max_digits=5, validators=apps.catalog.models.PERCENT_VALIDATORS)),
            ("advance_kind", models.CharField(choices=[("percent", "Foiz"), ("fixed", "Qat’iy summa")], max_length=10)),
            ("advance_value", models.DecimalField(decimal_places=2, max_digits=14, validators=[django.core.validators.MinValueValidator(0)])),
            ("plumber_response_minutes", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
        ], options={"constraints": [
            models.CheckConstraint(condition=models.Q(pk=1), name="single_service_center"),
            models.CheckConstraint(condition=models.Q(default_plumber_commission__gte=0, default_plumber_commission__lte=100, default_store_commission__gte=0, default_store_commission__lte=100), name="center_commissions_range"),
            models.CheckConstraint(condition=models.Q(advance_value__gte=0) & (~models.Q(advance_kind="percent") | models.Q(advance_value__lte=100)), name="center_advance_range"),
            models.CheckConstraint(condition=models.Q(plumber_response_minutes__gt=0), name="center_response_positive"),
        ]}),
        migrations.CreateModel(name="ContractTemplate", fields=identity() + timestamps() + [
            ("language", models.CharField(choices=apps.catalog.models.LANGUAGES, max_length=2)),
            ("version", models.PositiveIntegerField(validators=[django.core.validators.MinValueValidator(1)])),
            ("text", models.TextField()), ("is_active", models.BooleanField(default=True)),
        ], options={"ordering": ("language", "-version"), "constraints": [models.UniqueConstraint(fields=("language", "version"), name="unique_contract_template_version")]}),
    ]
