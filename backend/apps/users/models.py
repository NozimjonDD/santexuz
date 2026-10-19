from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from apps.catalog.models import LANGUAGES, PERCENT_VALIDATORS
from project_backend.base_model import BaseModel


class User(AbstractUser, BaseModel):
    class Role(models.TextChoices):
        CUSTOMER = "customer", "Mijoz"
        PLUMBER = "plumber", "Santexnik"
        STORE = "store", "Do‘kon"

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.CUSTOMER)
    telegram_id = models.BigIntegerField(null=True, blank=True, unique=True, validators=[MinValueValidator(1)])
    phone_number = models.CharField(max_length=20, blank=True, validators=[RegexValidator(r"^\+?[1-9]\d{6,14}$", "Telefon xalqaro formatda bo‘lishi kerak.")])
    phone_verified_at = models.DateTimeField(null=True, blank=True)
    language = models.CharField(max_length=2, choices=LANGUAGES, default="uz")

    class Meta(AbstractUser.Meta):
        db_table = "users_user"
        constraints = [models.CheckConstraint(condition=models.Q(telegram_id__isnull=True) | models.Q(telegram_id__gt=0), name="positive_telegram_user_id")]


class Consumer(BaseModel):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="consumer_profile",
        limit_choices_to={"role": User.Role.CUSTOMER},
    )
    address = models.TextField(blank=True)
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-90), MaxValueValidator(90)],
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-180), MaxValueValidator(180)],
    )

    class Meta:
        db_table = "users_consumer"
        constraints = [
            models.CheckConstraint(
                condition=models.Q(latitude__isnull=True) | models.Q(latitude__gte=-90, latitude__lte=90),
                name="consumer_latitude_range",
            ),
            models.CheckConstraint(
                condition=models.Q(longitude__isnull=True) | models.Q(longitude__gte=-180, longitude__lte=180),
                name="consumer_longitude_range",
            ),
        ]

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.CUSTOMER:
            raise ValidationError({"user": "Mijoz rolidagi akkauntni tanlang."})
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError("Kenglik va uzunlik birga kiritilishi kerak.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class PlumberProfile(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="plumber_profile", limit_choices_to={"role": User.Role.PLUMBER})
    regions = models.ManyToManyField("catalog.Region", related_name="plumbers")
    services = models.ManyToManyField("catalog.ServiceGroup", related_name="plumbers")
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PERCENT_VALIDATORS)
    experience_years = models.PositiveSmallIntegerField(default=0)
    photo = models.FileField(upload_to="plumbers/%Y/%m/", blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users_plumberprofile"
        constraints = [models.CheckConstraint(condition=models.Q(commission_rate__isnull=True) | models.Q(commission_rate__gte=0, commission_rate__lte=100), name="plumber_commission_range")]

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.PLUMBER:
            raise ValidationError({"user": "Santexnik rolidagi akkauntni tanlang."})

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.user.get_full_name() or self.user.username


class Store(BaseModel):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="store_profile", limit_choices_to={"role": User.Role.STORE})
    name = models.CharField(max_length=200)
    address = models.TextField()
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-90), MaxValueValidator(90)])
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True, validators=[MinValueValidator(-180), MaxValueValidator(180)])
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, validators=PERCENT_VALIDATORS)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "users_store"
        constraints = [
            models.CheckConstraint(condition=models.Q(commission_rate__isnull=True) | models.Q(commission_rate__gte=0, commission_rate__lte=100), name="store_commission_range"),
            models.CheckConstraint(condition=models.Q(latitude__isnull=True) | models.Q(latitude__gte=-90, latitude__lte=90), name="store_latitude_range"),
            models.CheckConstraint(condition=models.Q(longitude__isnull=True) | models.Q(longitude__gte=-180, longitude__lte=180), name="store_longitude_range"),
        ]

    def clean(self):
        super().clean()
        if self.user_id and self.user.role != User.Role.STORE:
            raise ValidationError({"user": "Do‘kon rolidagi akkauntni tanlang."})
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError("Kenglik va uzunlik birga kiritilishi kerak.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name
