"""Workflow writes go through staff REST actions, preserving service invariants."""
from django.contrib import admin

from .models import (Attachment, CashHandover, Contract, Delivery, DeliveryItem, Issue,
                     MaterialItem, Order, OrderEvent, Payment, Quote, Rating, Refund,
                     ServiceItem, Settlement)


class ReadOnlyDomainAdmin(admin.ModelAdmin):
    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(ReadOnlyDomainAdmin):
    list_display = ("id", "status", "customer", "plumber", "store", "created_at")
    list_filter = ("status", "region", "service_group", "is_urgent")
    search_fields = ("id", "address", "customer__username", "phone_snapshot")


for model in (ServiceItem, MaterialItem, Quote, Contract, Delivery, DeliveryItem, Payment,
              Refund, CashHandover, Settlement, Issue, Rating, Attachment, OrderEvent):
    admin.site.register(model, ReadOnlyDomainAdmin)
