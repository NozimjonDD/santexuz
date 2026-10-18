from django.db import transaction
from .audit import record


class AuditedAdminMixin:
    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        sensitive = {"password", "password1", "password2"}
        record(request.user, "admin.update" if change else "admin.create", obj,
               {"fields": [field for field in form.changed_data if field not in sensitive]})

    def delete_model(self, request, obj):
        with transaction.atomic():
            record(request.user, "admin.delete", obj)
            super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        with transaction.atomic():
            for obj in queryset:
                record(request.user, "admin.delete", obj)
            super().delete_queryset(request, queryset)
