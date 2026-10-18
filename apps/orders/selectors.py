from decimal import Decimal

from django.db.models import Avg, DecimalField, OuterRef, Prefetch, Q, Subquery, Sum, Value
from django.db.models.functions import Coalesce
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

from apps.users.models import PlumberProfile, Store, User
from .models import Contract, Order, Payment, Quote, Rating, Refund, Settlement


def orders_for(user):
    queryset = Order.objects.filter(is_deleted=False).select_related("customer", "plumber", "store", "region", "service_group")
    if user.is_staff:
        return queryset
    return queryset.filter(Q(customer=user) | Q(plumber=user) | Q(store=user))


def get_order(user, order_id):
    return get_object_or_404(orders_for(user), pk=order_id)


def current_quote(order):
    version = order.approved_version or order.quote_version
    if not version:
        return None
    cache = getattr(order, "_prefetched_objects_cache", {})
    if "quotes" in cache:
        return next((quote for quote in cache["quotes"] if quote.version == version), None)
    return order.quotes.filter(version=version).first()


def financial_queryset(queryset):
    """Read-only totals: correlated sums avoid fan-out across multiple journals."""
    output = DecimalField(max_digits=24, decimal_places=2)

    def total(model, **filters):
        rows = (model.objects.filter(order_id=OuterRef("pk"), **filters).order_by()
                .values("order_id").annotate(value=Sum("amount")).values("value"))
        return Coalesce(Subquery(rows, output_field=output), Value(Decimal("0.00")), output_field=output)

    return queryset.annotate(
        _finance_paid=total(Payment), _finance_refunded=total(Refund),
        _finance_plumber_paid=total(Settlement, partner="plumber"),
        _finance_store_paid=total(Settlement, partner="store"),
    ).prefetch_related("quotes")


def order_details(queryset):
    plumbers = (PlumberProfile.objects.select_related("user").annotate(
        rating=Avg("user__plumber_orders__rating__plumber_score", filter=Q(
            user__plumber_orders__is_deleted=False, user__plumber_orders__rating__approved=True,
            user__plumber_orders__rating__is_deleted=False)))
        .prefetch_related("regions", "services"))
    stores = Store.objects.annotate(rating=Avg("user__store_orders__rating__store_score", filter=Q(
        user__store_orders__is_deleted=False, user__store_orders__rating__approved=True,
        user__store_orders__rating__is_deleted=False)))
    return financial_queryset(queryset).prefetch_related(
        Prefetch("plumber__plumber_profile", queryset=plumbers),
        Prefetch("store__store_profile", queryset=stores),
        "service_items", "material_items",
        Prefetch("contracts", queryset=Contract.objects.select_related("quote")),
        Prefetch("payments", queryset=Payment.objects.select_related("received_by")),
        "refunds", "deliveries__items", "issues", "rating", "attachments", "events", "settlements",
    )


def eligible_plumbers(actor, order_id):
    if not actor.is_staff:
        raise PermissionDenied("Faqat xizmat markazi xodimi uchun.")
    order = get_order(actor, order_id)
    return User.objects.filter(
        role=User.Role.PLUMBER, is_active=True, is_deleted=False,
        plumber_profile__is_active=True, plumber_profile__is_deleted=False,
        plumber_profile__regions=order.region, plumber_profile__services=order.service_group,
    ).exclude(pk__in=order.rejected_plumber_ids).distinct().order_by("first_name", "last_name", "pk")


def sum_amount(queryset):
    return queryset.aggregate(total=Sum("amount"))["total"] or Decimal("0.00")


def financial_summary(order):
    # Services deliberately use fresh aggregates on locked, unannotated orders.
    # Only read querysets opt into snapshot totals, so mutations cannot reuse stale sums.
    quote = current_quote(order)
    paid = getattr(order, "_finance_paid", None)
    refunded = getattr(order, "_finance_refunded", None)
    if paid is None:
        paid = sum_amount(order.payments.all())
    if refunded is None:
        refunded = sum_amount(order.refunds.all())
    result = {"paid": paid, "refunded": refunded, "net_paid": paid - refunded,
              "total": quote.total if quote else Decimal("0.00"),
              "advance_required": quote.advance_required if quote else Decimal("0.00")}
    result["balance_due"] = max(result["total"] - result["net_paid"], Decimal("0.00"))
    if order.status == Order.Status.CANCELLED:
        result["balance_due"] = Decimal("0.00")
    for partner in ("plumber", "store"):
        due = Decimal(quote.snapshot.get(f"{partner}_net", "0")) if quote else Decimal("0")
        result[f"{partner}_net"] = due
        paid_to_partner = getattr(order, f"_finance_{partner}_paid", None)
        result[f"{partner}_paid"] = paid_to_partner if paid_to_partner is not None else sum_amount(order.settlements.filter(partner=partner))
        result[f"{partner}_due"] = Decimal("0.00") if order.status == Order.Status.CANCELLED else max(due - result[f"{partner}_paid"], Decimal("0"))
    return result
