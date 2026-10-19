from django.contrib import admin

from apps.catalog.models import ContractTemplate, Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.common.admin_mixins import AuditedAdminMixin


class CatalogAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "is_active")
    list_filter = ("is_active",)
    search_fields = ("name",)


admin.site.register(Region, CatalogAdmin)
admin.site.register(ServiceGroup, CatalogAdmin)
admin.site.register(Service, CatalogAdmin)
admin.site.register(Material, CatalogAdmin)


@admin.register(ServiceRate)
class ServiceRateAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("region", "service", "unit_price", "urgent_fee")
    list_filter = ("region",)
    autocomplete_fields = ("region", "service")


@admin.register(ServiceCenter)
class ServiceCenterAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("name", "phone", "opening_time", "closing_time")

    def has_add_permission(self, request):
        return not ServiceCenter.objects.exists() and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ContractTemplate)
class ContractTemplateAdmin(AuditedAdminMixin, admin.ModelAdmin):
    list_display = ("language", "version", "is_active", "created_at")
    list_filter = ("language", "is_active")

    def get_readonly_fields(self, request, obj=None):
        return ("language", "version", "text") if obj else ()

    def has_delete_permission(self, request, obj=None):
        return False
