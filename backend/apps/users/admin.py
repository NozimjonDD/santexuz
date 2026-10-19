from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from apps.common.admin_mixins import AuditedAdminMixin
from apps.users.models import Consumer, PlumberProfile, Store, User


@admin.register(User)
class UserAdmin(AuditedAdminMixin, DjangoUserAdmin):
    list_display = ("username", "role", "telegram_id", "phone_number", "is_staff", "is_active")
    list_filter = ("role", "is_staff", "is_active")
    fieldsets = DjangoUserAdmin.fieldsets + (("Mini App", {"fields": ("role", "telegram_id", "phone_number", "phone_verified_at", "language")}),)
    add_fieldsets = DjangoUserAdmin.add_fieldsets + (("Mini App", {"fields": ("role", "telegram_id", "phone_number", "language")}),)
    search_fields = ("username", "first_name", "last_name", "phone_number", "telegram_id")
    readonly_fields = ("phone_verified_at",)

    def get_readonly_fields(self, request, obj=None):
        return (*self.readonly_fields, "role") if obj else self.readonly_fields

    def save_model(self, request, obj, form, change):
        if change and {"phone_number", "telegram_id"}.intersection(form.changed_data):
            obj.phone_verified_at = None
        super().save_model(request, obj, form, change)

    def log_change(self, request, obj, message):
        from apps.common.audit import record
        record(request.user, "admin.account_changed", obj)
        return super().log_change(request, obj, message)


@admin.register(PlumberProfile)
class PlumberProfileAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("user", "experience_years", "commission_rate", "is_active")
    list_filter = ("is_active", "regions", "services")
    filter_horizontal = ("regions", "services")
    autocomplete_fields = ("user",)

    def get_readonly_fields(self, request, obj=None):
        return ("user",) if obj else ()


@admin.register(Consumer)
class ConsumerAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("user", "address", "latitude", "longitude")
    search_fields = ("user__username", "user__first_name", "user__last_name", "address")
    autocomplete_fields = ("user",)

    def get_readonly_fields(self, request, obj=None):
        return ("user",) if obj else ()


@admin.register(Store)
class StoreAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "user", "commission_rate", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name", "address")
    autocomplete_fields = ("user",)

    def get_readonly_fields(self, request, obj=None):
        return ("user",) if obj else ()
