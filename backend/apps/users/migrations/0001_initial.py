import django.contrib.auth.models
import django.contrib.auth.validators
import django.core.validators
import django.db.models.deletion
import django.utils.timezone
from django.conf import settings
from django.db import migrations, models

import apps.catalog.models


def identity():
    return [("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID"))]


def timestamps():
    return [("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True))]


class Migration(migrations.Migration):
    initial = True
    dependencies = [("auth", "0012_alter_user_first_name_max_length"), ("catalog", "0001_initial")]
    operations = [
        migrations.CreateModel(name="User", fields=identity() + [
            ("password", models.CharField(max_length=128, verbose_name="password")),
            ("last_login", models.DateTimeField(blank=True, null=True, verbose_name="last login")),
            ("is_superuser", models.BooleanField(default=False, help_text="Designates that this user has all permissions without explicitly assigning them.", verbose_name="superuser status")),
            ("username", models.CharField(error_messages={"unique": "A user with that username already exists."}, help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.", max_length=150, unique=True, validators=[django.contrib.auth.validators.UnicodeUsernameValidator()], verbose_name="username")),
            ("first_name", models.CharField(blank=True, max_length=150, verbose_name="first name")),
            ("last_name", models.CharField(blank=True, max_length=150, verbose_name="last name")),
            ("email", models.EmailField(blank=True, max_length=254, verbose_name="email address")),
            ("is_staff", models.BooleanField(default=False, help_text="Designates whether the user can log into this admin site.", verbose_name="staff status")),
            ("is_active", models.BooleanField(default=True, help_text="Designates whether this user should be treated as active. Unselect this instead of deleting accounts.", verbose_name="active")),
            ("date_joined", models.DateTimeField(default=django.utils.timezone.now, verbose_name="date joined")),
            ("role", models.CharField(choices=[("customer", "Mijoz"), ("plumber", "Santexnik"), ("store", "Do‘kon")], default="customer", max_length=20)),
            ("telegram_id", models.BigIntegerField(blank=True, null=True, unique=True, validators=[django.core.validators.MinValueValidator(1)])),
            ("phone_number", models.CharField(blank=True, max_length=20, validators=[django.core.validators.RegexValidator(r"^\+?[1-9]\d{6,14}$", "Telefon xalqaro formatda bo‘lishi kerak.")])),
            ("phone_verified_at", models.DateTimeField(blank=True, null=True)),
            ("language", models.CharField(choices=apps.catalog.models.LANGUAGES, default="uz", max_length=2)),
            ("groups", models.ManyToManyField(blank=True, help_text="The groups this user belongs to. A user will get all permissions granted to each of their groups.", related_name="user_set", related_query_name="user", to="auth.group", verbose_name="groups")),
            ("user_permissions", models.ManyToManyField(blank=True, help_text="Specific permissions for this user.", related_name="user_set", related_query_name="user", to="auth.permission", verbose_name="user permissions")),
        ], options={"verbose_name": "user", "verbose_name_plural": "users", "abstract": False,
                    "constraints": [models.CheckConstraint(condition=models.Q(telegram_id__isnull=True) | models.Q(telegram_id__gt=0), name="positive_telegram_user_id")]},
           managers=[("objects", django.contrib.auth.models.UserManager())]),
        migrations.CreateModel(name="PlumberProfile", fields=identity() + timestamps() + [
            ("commission_rate", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=apps.catalog.models.PERCENT_VALIDATORS)),
            ("experience_years", models.PositiveSmallIntegerField(default=0)),
            ("photo", models.FileField(blank=True, upload_to="plumbers/%Y/%m/")),
            ("is_active", models.BooleanField(default=True)),
            ("user", models.OneToOneField(limit_choices_to={"role": "plumber"}, on_delete=django.db.models.deletion.PROTECT, related_name="plumber_profile", to=settings.AUTH_USER_MODEL)),
            ("regions", models.ManyToManyField(related_name="plumbers", to="catalog.region")),
            ("services", models.ManyToManyField(related_name="plumbers", to="catalog.servicegroup")),
        ], options={"constraints": [models.CheckConstraint(condition=models.Q(commission_rate__isnull=True) | models.Q(commission_rate__gte=0, commission_rate__lte=100), name="plumber_commission_range")]}),
        migrations.CreateModel(name="Store", fields=identity() + timestamps() + [
            ("name", models.CharField(max_length=200)), ("address", models.TextField()),
            ("latitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-90), django.core.validators.MaxValueValidator(90)])),
            ("longitude", models.DecimalField(blank=True, decimal_places=6, max_digits=9, null=True, validators=[django.core.validators.MinValueValidator(-180), django.core.validators.MaxValueValidator(180)])),
            ("commission_rate", models.DecimalField(blank=True, decimal_places=2, max_digits=5, null=True, validators=apps.catalog.models.PERCENT_VALIDATORS)),
            ("is_active", models.BooleanField(default=True)),
            ("user", models.OneToOneField(limit_choices_to={"role": "store"}, on_delete=django.db.models.deletion.PROTECT, related_name="store_profile", to=settings.AUTH_USER_MODEL)),
        ], options={"constraints": [
            models.CheckConstraint(condition=models.Q(commission_rate__isnull=True) | models.Q(commission_rate__gte=0, commission_rate__lte=100), name="store_commission_range"),
            models.CheckConstraint(condition=models.Q(latitude__isnull=True) | models.Q(latitude__gte=-90, latitude__lte=90), name="store_latitude_range"),
            models.CheckConstraint(condition=models.Q(longitude__isnull=True) | models.Q(longitude__gte=-180, longitude__lte=180), name="store_longitude_range"),
        ]}),
    ]
