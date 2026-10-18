from decimal import Decimal

from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

from project_backend.base_model import BaseModel


LANGUAGES = (("uz", "O‘zbekcha"), ("ru", "Русский"), ("en", "English"))
PERCENT_VALIDATORS = [MinValueValidator(Decimal("0")), MaxValueValidator(Decimal("100"))]


def validate_working_days(value):
    if not isinstance(value, list) or not value or any(type(day) is not int or not 0 <= day <= 6 for day in value):
        raise ValidationError("Ish kunlari 0 (dushanba) dan 6 (yakshanba) gacha bo‘lgan ro‘yxat bo‘lishi kerak.")
    if len(value) != len(set(value)):
        raise ValidationError("Ish kunlari takrorlanmasligi kerak.")


class Region(BaseModel):
    name = models.CharField(max_length=150)
    code = models.SlugField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "catalog_region"
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class ServiceGroup(BaseModel):
    name = models.CharField(max_length=150)
    name_ru = models.CharField(max_length=150, blank=True)
    name_en = models.CharField(max_length=150, blank=True)
    code = models.SlugField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "catalog_servicegroup"
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class Service(BaseModel):
    group = models.ForeignKey(ServiceGroup, on_delete=models.PROTECT, related_name="services")
    name = models.CharField(max_length=200)
    name_ru = models.CharField(max_length=200, blank=True)
    name_en = models.CharField(max_length=200, blank=True)
    unit = models.CharField(max_length=30)
    warranty_days = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "catalog_service"
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class ServiceRate(BaseModel):
    region = models.ForeignKey(Region, on_delete=models.PROTECT, related_name="rates")
    service = models.ForeignKey(Service, on_delete=models.PROTECT, related_name="rates")
    unit_price = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    urgent_fee = models.DecimalField(max_digits=14, decimal_places=2, default=0, validators=[MinValueValidator(0)])

    class Meta:
        db_table = "catalog_servicerate"
        constraints = [
            models.UniqueConstraint(fields=("region", "service"), name="unique_region_service_rate"),
            models.CheckConstraint(condition=models.Q(unit_price__gte=0, urgent_fee__gte=0), name="nonnegative_service_rate"),
        ]

    def __str__(self):
        return f"{self.region}: {self.service}"


class Material(BaseModel):
    name = models.CharField(max_length=200)
    unit = models.CharField(max_length=30)
    brand = models.CharField(max_length=150, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "catalog_material"
        ordering = ("name", "id")

    def __str__(self):
        return self.name


class ServiceCenter(BaseModel):
    class AdvanceKind(models.TextChoices):
        PERCENT = "percent", "Foiz"
        FIXED = "fixed", "Qat’iy summa"

    name = models.CharField(max_length=200)
    address = models.TextField()
    phone = models.CharField(max_length=20)
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    working_days = models.JSONField(validators=[validate_working_days])
    default_plumber_commission = models.DecimalField(max_digits=5, decimal_places=2, validators=PERCENT_VALIDATORS)
    default_store_commission = models.DecimalField(max_digits=5, decimal_places=2, validators=PERCENT_VALIDATORS)
    advance_kind = models.CharField(max_length=10, choices=AdvanceKind.choices)
    advance_value = models.DecimalField(max_digits=14, decimal_places=2, validators=[MinValueValidator(0)])
    plumber_response_minutes = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        db_table = "catalog_servicecenter"
        constraints = [
            models.CheckConstraint(condition=models.Q(pk=1), name="single_service_center"),
            models.CheckConstraint(condition=models.Q(default_plumber_commission__gte=0, default_plumber_commission__lte=100, default_store_commission__gte=0, default_store_commission__lte=100), name="center_commissions_range"),
            models.CheckConstraint(condition=models.Q(advance_value__gte=0) & (~models.Q(advance_kind="percent") | models.Q(advance_value__lte=100)), name="center_advance_range"),
            models.CheckConstraint(condition=models.Q(plumber_response_minutes__gt=0), name="center_response_positive"),
        ]

    def clean(self):
        super().clean()
        validate_working_days(self.working_days)
        if self.opening_time and self.closing_time and self.opening_time >= self.closing_time:
            raise ValidationError({"closing_time": "Yopilish vaqti ochilish vaqtidan keyin bo‘lishi kerak."})
        if self.advance_kind == self.AdvanceKind.PERCENT and self.advance_value > 100:
            raise ValidationError({"advance_value": "Avans foizi 100 dan oshmasligi kerak."})

    def save(self, *args, **kwargs):
        self.pk = 1
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class ContractTemplate(BaseModel):
    language = models.CharField(max_length=2, choices=LANGUAGES)
    version = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    text = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "catalog_contracttemplate"
        ordering = ("language", "-version")
        constraints = [models.UniqueConstraint(fields=("language", "version"), name="unique_contract_template_version")]

    def clean(self):
        super().clean()
        if self.pk:
            original = type(self).objects.filter(pk=self.pk).values("language", "version", "text").first()
            if original and any(original[field] != getattr(self, field) for field in original):
                raise ValidationError("Andoza matni o‘zgartirilmaydi; yangi versiya yarating.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.language} v{self.version}"
