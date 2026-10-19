"""Order application services. Every mutation serializes on the parent order row."""
from datetime import timedelta
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django.db import IntegrityError, transaction
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework.exceptions import PermissionDenied, ValidationError

from apps.catalog.models import ContractTemplate, Material, Region, ServiceCenter, ServiceGroup, ServiceRate
from apps.common.audit import record
from apps.users.models import User
from .models import (Attachment, CashHandover, Contract, Delivery, DeliveryItem, Issue, MaterialItem,
                     Order, OrderEvent, Payment, Quote, Rating, Refund, ServiceItem, Settlement)
from .selectors import eligible_plumbers, financial_summary, sum_amount

ZERO = Decimal("0.00")
CENT = Decimal("0.01")
TERMINAL = {Order.Status.CANCELLED, Order.Status.CLOSED}


def money(value, *, positive=False):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Noto‘g‘ri pul qiymati.")
    if not result.is_finite() or result < 0 or (positive and result <= 0) or result >= Decimal("100000000000000"):
        raise ValidationError("Pul qiymati ruxsat etilgan oraliqda emas.")
    if result != result.quantize(CENT):
        raise ValidationError("Pul qiymati ikki kasrdan oshmasin.")
    return result.quantize(CENT)


def quantity(value):
    try:
        result = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Miqdor noto‘g‘ri.")
    if not result.is_finite() or result <= 0 or result >= Decimal("1000000000") or result != result.quantize(Decimal("0.001")):
        raise ValidationError("Miqdor musbat va uch kasrdan oshmagan bo‘lishi kerak.")
    return result


def _staff(actor):
    if not actor.is_staff:
        raise PermissionDenied("Faqat xizmat markazi xodimi uchun.")


def _customer(actor, order):
    if actor.pk != order.customer_id:
        raise PermissionDenied("Faqat ushbu buyurtma mijozi uchun.")


def _plumber(actor, order):
    if actor.pk != order.plumber_id or not order.plumber_accepted:
        raise PermissionDenied("Faqat buyurtmani qabul qilgan santexnik uchun.")


def _store(actor, order):
    if actor.pk != order.store_id or not order.store_accepted:
        raise PermissionDenied("Faqat buyurtmani qabul qilgan do‘kon uchun.")


def _lock(order_id):
    return get_object_or_404(Order.objects.filter(is_deleted=False).select_for_update(of=("self",)).select_related("customer", "plumber", "store", "region", "service_group"), pk=order_id)


def _state(order, *statuses):
    if order.status not in statuses:
        raise ValidationError({"status": f"Bu amal {order.status} holatida mumkin emas."})


def _editable(order):
    if order.preparation_started_at or order.work_started_at or order.status in TERMINAL | {Order.Status.DISPUTED, Order.Status.REJECTED}:
        raise ValidationError("Smetani bu bosqichda o‘zgartirib bo‘lmaydi.")


def _event(actor, order, action, payload=None, *, notify=True):
    payload = payload or {}
    order.save()
    OrderEvent.objects.create(order=order, actor=actor, action=action, status=order.status, payload=payload)
    record(actor, action, order, payload)
    if notify:
        from apps.tg_bot.services import enqueue
        enqueue(order.customer, action, order, payload=payload)
    if action in {"order.created", "order.plumber_rejected", "order.store_rejected", "order.quote_rejected", "order.dispute_opened"}:
        from apps.tg_bot.services import enqueue
        for recipient in User.objects.filter(is_active=True, is_staff=True, is_deleted=False):
            enqueue(recipient, action, order, payload={})
    return order


def _invalidate(order):
    order.approved_version = None


def _settings():
    try:
        return ServiceCenter.objects.get(pk=1, is_deleted=False)
    except ServiceCenter.DoesNotExist:
        raise ValidationError("Xizmat markazi sozlamalari hali kiritilmagan.")


def _open_now(center):
    now = timezone.localtime()
    if now.weekday() not in center.working_days:
        return False
    return center.opening_time <= now.time().replace(tzinfo=None) < center.closing_time


def _current_quote(order, *, approved=False):
    version = order.approved_version if approved else order.quote_version
    if not version:
        raise ValidationError("Tasdiqlangan smeta mavjud emas." if approved else "Smeta mavjud emas.")
    return get_object_or_404(Quote, order=order, version=version)


def _ready_to_start(order):
    quote = _current_quote(order, approved=True)
    if quote.version != order.quote_version or not Contract.objects.filter(quote=quote, signed_at__isnull=False).exists():
        raise ValidationError("Joriy smeta tasdiqlanib, to‘rt tomon shartnomasi imzolanishi kerak.")
    net_paid = financial_summary(order)["net_paid"]
    if net_paid > quote.total:
        raise ValidationError("Yangi smetadan ortiqcha to‘lov avval qaytarilishi kerak.")
    if net_paid < quote.advance_required:
        raise ValidationError("Talab qilingan avans to‘liq to‘lanmagan.")
    return quote


@transaction.atomic
def create_order(actor, region_id, service_group_id, address, latitude, longitude, consent, is_urgent=False, description=""):
    if actor.role != User.Role.CUSTOMER:
        raise PermissionDenied("So‘rovni faqat mijoz yuborishi mumkin.")
    if not consent or not actor.phone_number or not actor.phone_verified_at:
        raise ValidationError("Telegram telefoni va ma’lumotlarni ulashish roziligi zarur.")
    if not address.strip():
        raise ValidationError({"address": "Manzil majburiy."})
    try:
        lat, lon = Decimal(str(latitude)), Decimal(str(longitude))
    except (InvalidOperation, TypeError, ValueError):
        raise ValidationError("Lokatsiya noto‘g‘ri.")
    if not lat.is_finite() or not lon.is_finite() or not (-90 <= lat <= 90 and -180 <= lon <= 180):
        raise ValidationError("Lokatsiya noto‘g‘ri.")
    if is_urgent and not _open_now(_settings()):
        raise ValidationError("Shoshilinch so‘rov faqat markaz ish vaqtida qabul qilinadi.")
    order = Order.objects.create(customer=actor, region=get_object_or_404(Region, pk=region_id, is_active=True, is_deleted=False),
                                 service_group=get_object_or_404(ServiceGroup, pk=service_group_id, is_active=True, is_deleted=False),
                                 address=address.strip(), latitude=lat, longitude=lon, description=description,
                                 consent_at=timezone.now(), phone_snapshot=actor.phone_number, is_urgent=is_urgent)
    return _event(actor, order, "order.created")


@transaction.atomic
def confirm_urgent(actor, order_id, confirmed):
    _staff(actor)
    order = _lock(order_id)
    _state(order, Order.Status.REQUESTED)
    if confirmed and (not order.is_urgent or not _open_now(_settings())):
        raise ValidationError("Shoshilinch so‘rov ish vaqtida tasdiqlanadi.")
    order.urgent_confirmed = bool(confirmed)
    return _event(actor, order, "order.urgent_confirmed")


@transaction.atomic
def assign_plumber(actor, order_id, plumber_id):
    _staff(actor)
    order = _lock(order_id)
    _state(order, Order.Status.REQUESTED, Order.Status.ASSIGNED, Order.Status.REJECTED, Order.Status.ACCEPTED, Order.Status.INSPECTION, Order.Status.ESTIMATE)
    if order.preparation_started_at or order.work_started_at or financial_summary(order)["net_paid"] > 0:
        raise ValidationError("Qayta tayinlashdan avval olingan pul qaytarilsin; boshlangan ish/tayyorlashda almashtirish mumkin emas.")
    if order.is_urgent and not order.urgent_confirmed:
        raise ValidationError("Shoshilinchlik avval admin tomonidan tasdiqlanishi kerak.")
    plumber = get_object_or_404(eligible_plumbers(actor, order.pk), pk=plumber_id)
    order.plumber = plumber
    order.plumber_accepted = False
    order.store = None
    order.store_accepted = False
    order.response_due_at = timezone.now() + timedelta(minutes=_settings().plumber_response_minutes)
    order.response_alerted_at = None
    order.inspection_at = None
    order.work_starts_at = None
    order.work_ends_at = None
    _invalidate(order)
    order.status = Order.Status.ASSIGNED
    _event(actor, order, "order.plumber_assigned", notify=False)
    from apps.tg_bot.services import enqueue
    enqueue(plumber, "order.plumber_assigned", order)
    return order


@transaction.atomic
def respond_plumber(actor, order_id, accept, reason=""):
    order = _lock(order_id)
    if actor.pk != order.plumber_id:
        raise PermissionDenied("Santexnik buyurtmaga biriktirilmagan.")
    if accept and order.plumber_accepted:
        return order
    _state(order, Order.Status.ASSIGNED)
    order.response_due_at = None
    if accept:
        order.plumber_accepted = True
        order.status = Order.Status.ACCEPTED
        return _event(actor, order, "order.plumber_accepted")
    if not reason.strip():
        raise ValidationError({"reason": "Rad etish sababi kerak."})
    order.plumber = None
    order.status = Order.Status.REQUESTED
    return _event(actor, order, "order.plumber_rejected", {"reason": reason}, notify=False)


@transaction.atomic
def schedule_inspection(actor, order_id, inspection_at):
    order = _lock(order_id)
    _plumber(actor, order)
    _state(order, Order.Status.ACCEPTED, Order.Status.INSPECTION)
    if inspection_at <= timezone.now():
        raise ValidationError("Ko‘rik vaqti kelajakda bo‘lishi kerak.")
    order.inspection_at = inspection_at
    order.status = Order.Status.INSPECTION
    return _event(actor, order, "order.inspection_scheduled", {"inspection_at": inspection_at.isoformat()})


@transaction.atomic
def submit_estimate(actor, order_id, services, materials):
    order = _lock(order_id)
    _plumber(actor, order)
    _editable(order)
    _state(order, Order.Status.INSPECTION, Order.Status.ESTIMATE, Order.Status.STORE_ASSIGNED, Order.Status.STORE_ACCEPTED, Order.Status.QUOTED, Order.Status.APPROVED)
    if actor.pk in order.rejected_plumber_ids:
        raise ValidationError("Rad etilgan smetani o‘sha usta qayta yubora olmaydi.")
    if not services:
        raise ValidationError({"services": "Kamida bitta xizmat zarur."})
    if order.deliveries.exists():
        raise ValidationError("Yetkazish boshlangan smetani almashtirib bo‘lmaydi.")
    order.service_items.all().delete()
    order.material_items.all().delete()
    seen = set()
    for item in services:
        service_id = item["service_id"]
        if service_id in seen:
            raise ValidationError("Xizmat bir marta kiritilishi kerak.")
        seen.add(service_id)
        rate = get_object_or_404(ServiceRate.objects.select_related("service"), region=order.region, is_deleted=False,
                                 service_id=service_id, service__group=order.service_group, service__is_active=True, service__is_deleted=False)
        service = rate.service
        ServiceItem.objects.create(order=order, service=service, name=service.name, unit=service.unit,
                                   quantity=quantity(item["quantity"]), unit_price=rate.unit_price,
                                   urgent_fee=rate.urgent_fee, warranty_days=service.warranty_days)
    for item in materials:
        material = get_object_or_404(Material, pk=item["material_id"], is_active=True, is_deleted=False) if item.get("material_id") else None
        name = material.name if material else str(item.get("name", "")).strip()
        unit = material.unit if material else str(item.get("unit", "")).strip()
        if not name or not unit:
            raise ValidationError("Erkin material uchun nom va birlik zarur.")
        MaterialItem.objects.create(order=order, material=material, name=name, unit=unit,
                                    brand=item.get("brand", material.brand if material else ""), note=item.get("note", ""),
                                    quantity=quantity(item["quantity"]))
    _invalidate(order)
    order.status = Order.Status.ESTIMATE
    order.store = None
    order.store_accepted = False
    return _event(actor, order, "order.estimate_submitted")


@transaction.atomic
def assign_store(actor, order_id, store_id):
    _staff(actor)
    order = _lock(order_id)
    _editable(order)
    _state(order, Order.Status.ESTIMATE, Order.Status.STORE_ASSIGNED, Order.Status.STORE_ACCEPTED, Order.Status.QUOTED, Order.Status.APPROVED)
    store = get_object_or_404(User, pk=store_id, role=User.Role.STORE, is_active=True, is_deleted=False, store_profile__is_active=True, store_profile__is_deleted=False)
    order.store = store
    order.store_accepted = False
    order.material_items.update(unit_price=None, available=False, replacement_name="", supply_minutes=0)
    _invalidate(order)
    order.status = Order.Status.STORE_ASSIGNED
    _event(actor, order, "order.store_assigned")
    from apps.tg_bot.services import enqueue
    enqueue(store, "order.store_assigned", order)
    return order


@transaction.atomic
def respond_store(actor, order_id, accept, reason=""):
    order = _lock(order_id)
    if actor.pk != order.store_id:
        raise PermissionDenied("Do‘kon buyurtmaga biriktirilmagan.")
    if accept and order.store_accepted:
        return order
    _state(order, Order.Status.STORE_ASSIGNED)
    if not accept and not reason.strip():
        raise ValidationError("Rad etish sababi kerak.")
    order.store_accepted = bool(accept)
    order.status = Order.Status.STORE_ACCEPTED if accept else Order.Status.ESTIMATE
    if not accept:
        order.store = None
    return _event(actor, order, "order.store_accepted" if accept else "order.store_rejected", {"reason": reason})


def _build_quote(order):
    center = _settings()
    service_rows = [{"id": row.pk, "service_id": row.service_id, "name": row.name, "unit": row.unit,
                     "quantity": str(row.quantity), "unit_price": str(row.unit_price), "warranty_days": row.warranty_days,
                     "subtotal": str(money((row.quantity * row.unit_price).quantize(CENT, ROUND_HALF_UP)))} for row in order.service_items.all()]
    material_rows = [{"id": row.pk, "material_id": row.material_id, "name": row.replacement_name or row.name,
                      "original_name": row.name, "unit": row.unit, "brand": row.brand, "quantity": str(row.quantity),
                      "unit_price": str(row.unit_price), "available": row.available, "supply_minutes": row.supply_minutes,
                      "subtotal": str(money((row.quantity * row.unit_price).quantize(CENT, ROUND_HALF_UP)))} for row in order.material_items.all()]
    service_total = sum((Decimal(row["subtotal"]) for row in service_rows), ZERO)
    material_total = sum((Decimal(row["subtotal"]) for row in material_rows), ZERO)
    # A call has one urgent flat surcharge. Multiple services use the highest configured fee.
    urgent_fee = max((row.urgent_fee for row in order.service_items.all()), default=ZERO) if order.urgent_confirmed else ZERO
    total = money(service_total + material_total + order.delivery_fee + urgent_fee)
    if total <= 0:
        raise ValidationError("Jami narx musbat bo‘lishi kerak.")
    plumber_rate = order.plumber.plumber_profile.commission_rate
    store_rate = order.store.store_profile.commission_rate
    plumber_rate = center.default_plumber_commission if plumber_rate is None else plumber_rate
    store_rate = center.default_store_commission if store_rate is None else store_rate
    plumber_commission = (service_total * plumber_rate / 100).quantize(CENT, ROUND_HALF_UP)
    store_commission = (material_total * store_rate / 100).quantize(CENT, ROUND_HALF_UP)
    advance = (total * center.advance_value / 100 if center.advance_kind == "percent" else center.advance_value).quantize(CENT, ROUND_HALF_UP)
    advance = min(advance, total)
    from apps.common.routing import travel_minutes
    road_minutes = travel_minutes(order.store.store_profile, order)
    order.quote_version += 1
    _invalidate(order)
    snapshot = {"services": service_rows, "materials": material_rows, "currency": "UZS", "vat_included": True,
                "service_total": str(service_total), "material_total": str(material_total), "delivery_fee": str(order.delivery_fee),
                "urgent_fee": str(urgent_fee), "platform_fee": "0.00", "total": str(total), "advance_required": str(advance),
                "plumber_rate": str(plumber_rate), "store_rate": str(store_rate), "plumber_commission": str(plumber_commission),
                "store_commission": str(store_commission), "plumber_net": str(service_total + urgent_fee - plumber_commission),
                "store_net": str(material_total + order.delivery_fee - store_commission),
                "preparation_minutes": order.preparation_minutes, "travel_minutes": road_minutes,
                "estimated_delivery_minutes": order.preparation_minutes + road_minutes}
    return Quote.objects.create(order=order, version=order.quote_version, snapshot=snapshot, total=total, advance_required=advance)


@transaction.atomic
def price_materials(actor, order_id, items, delivery_fee, preparation_minutes):
    order = _lock(order_id)
    _store(actor, order)
    _editable(order)
    _state(order, Order.Status.STORE_ACCEPTED, Order.Status.QUOTED, Order.Status.APPROVED)
    rows = {row.pk: row for row in order.material_items.all()}
    if len(items) != len(rows) or {item["id"] for item in items} != set(rows):
        raise ValidationError("Har bir material narxi aynan bir marta kiritilishi kerak.")
    for item in items:
        row = rows[item["id"]]
        row.unit_price = money(item["unit_price"])
        row.available = bool(item["available"])
        row.replacement_name = str(item.get("replacement_name", "")).strip()
        row.supply_minutes = int(item.get("supply_minutes", 0))
        if row.supply_minutes < 0 or (not row.available and not row.replacement_name and row.supply_minutes <= 0):
            raise ValidationError("Mavjud bo‘lmagan mahsulotga muqobil yoki olib kelish muddati kerak.")
        row.save()
    order.delivery_fee = money(delivery_fee)
    order.preparation_minutes = int(preparation_minutes)
    if order.preparation_minutes < 0:
        raise ValidationError("Tayyorlash muddati manfiy bo‘lmasin.")
    quote = _build_quote(order)
    order.status = Order.Status.QUOTED
    return _event(actor, order, "order.quote_published", {"quote_version": quote.version, "estimated_delivery_minutes": quote.snapshot["estimated_delivery_minutes"]})


@transaction.atomic
def approve_quote(actor, order_id, quote_version):
    order = _lock(order_id)
    _customer(actor, order)
    if quote_version != order.quote_version:
        raise ValidationError({"quote_version": "Smeta yangilangan. Yangi versiyani ko‘rib chiqing."})
    if order.approved_version == order.quote_version and order.status == Order.Status.APPROVED:
        return order
    _state(order, Order.Status.QUOTED)
    quote = _current_quote(order)
    if financial_summary(order)["net_paid"] > quote.total:
        raise ValidationError("Yangi smetadagi ortiqcha to‘lovni avval admin qaytarsin.")
    template = ContractTemplate.objects.filter(language=actor.language, is_active=True, is_deleted=False).order_by("-version").first()
    if not template:
        raise ValidationError("Tanlangan tilda shartnoma andozasi kiritilmagan.")
    if not order.work_starts_at or not order.work_ends_at:
        raise ValidationError("Santexnik avval taxminiy ish jadvalini kiritsin.")
    Contract.objects.get_or_create(quote=quote, defaults={"order": order, "language": template.language,
        "template_version": template.version, "text_snapshot": template.text,
        "parties_snapshot": {"customer_id": order.customer_id, "customer": order.customer.get_full_name(),
            "plumber_id": order.plumber_id, "plumber": order.plumber.get_full_name(), "store_id": order.store_id,
            "store": order.store.store_profile.name, "center": center_name(), "address": order.address,
            "phone": order.phone_snapshot, "work_starts_at": order.work_starts_at.isoformat(),
            "work_ends_at": order.work_ends_at.isoformat()}})
    order.approved_version = quote.version
    order.status = Order.Status.APPROVED
    return _event(actor, order, "order.quote_approved", {"quote_version": quote.version})


def center_name():
    return _settings().name


@transaction.atomic
def reject_quote(actor, order_id, quote_version, reason=""):
    order = _lock(order_id)
    _customer(actor, order)
    if quote_version != order.quote_version:
        raise ValidationError({"quote_version": "Smeta yangilangan. Yangi versiyani ko‘rib chiqing."})
    _state(order, Order.Status.QUOTED)
    order.rejected_plumber_ids = sorted(set(order.rejected_plumber_ids + [order.plumber_id]))
    _invalidate(order)
    order.status = Order.Status.REJECTED
    return _event(actor, order, "order.quote_rejected", {"reason": reason})


@transaction.atomic
def sign_contract(actor, order_id):
    _staff(actor)
    order = _lock(order_id)
    _state(order, Order.Status.APPROVED)
    contract = get_object_or_404(Contract, quote=_current_quote(order, approved=True))
    if not contract.signed_at:
        contract.signed_at = timezone.now()
        contract.signed_by = actor
        contract.save()
        _event(actor, order, "order.contract_signed", {"contract_id": contract.pk})
    return order


def _idempotent(model, key, order, values):
    if not key or len(key) > 128:
        raise ValidationError("Idempotency kaliti majburiy (1–128 belgi).")
    existing = model.objects.filter(idempotency_key=key).first()
    if existing:
        if existing.order_id != order.pk or any(getattr(existing, name) != value for name, value in values.items()):
            raise ValidationError("Bu idempotency kaliti boshqa operatsiya uchun ishlatilgan.")
    return existing


def _create_journal(model, **values):
    # Different order locks can still race on the journal's global unique key.
    try:
        with transaction.atomic():
            return model.objects.create(**values)
    except IntegrityError:
        raise ValidationError({"idempotency_key": "Bu kalit boshqa operatsiyada ishlatilgan yoki yozuv bilan ziddiyat bor."}) from None


@transaction.atomic
def record_payment(actor, order_id, amount, method, kind, idempotency_key):
    order = _lock(order_id)
    if not actor.is_staff:
        _plumber(actor, order)
    amount = money(amount, positive=True)
    if method not in {"cash", "terminal"} or kind not in {"advance", "balance"}:
        raise ValidationError("To‘lov turi noto‘g‘ri.")
    existing = _idempotent(Payment, idempotency_key, order, {"amount": amount, "method": method, "kind": kind, "received_by_id": actor.pk})
    if existing:
        return existing
    if order.status in TERMINAL | {Order.Status.DISPUTED, Order.Status.REJECTED}:
        raise ValidationError("Bu holatda to‘lov qabul qilinmaydi.")
    quote = _current_quote(order, approved=True)
    if not Contract.objects.filter(quote=quote, signed_at__isnull=False).exists():
        raise ValidationError("Joriy shartnoma imzolanmagan.")
    summary = financial_summary(order)
    if amount > summary["balance_due"]:
        raise ValidationError("To‘lov qarzdorlikdan oshmasin.")
    if kind == "balance" and not order.customer_accepted_at:
        raise ValidationError("Qoldiq to‘lov mijoz ishni tasdiqlagandan keyin olinadi.")
    if kind == "advance" and summary["net_paid"] + amount > quote.advance_required:
        raise ValidationError("Avans joriy smetadagi talabdan oshmasin.")
    payment = _create_journal(Payment, order=order, amount=amount, method=method, kind=kind, received_by=actor, idempotency_key=idempotency_key)
    if order.customer_accepted_at and summary["net_paid"] + amount == quote.total:
        order.status = Order.Status.CLOSED
    _event(actor, order, "order.payment_received", {"payment_id": payment.pk, "amount": str(amount), "method": method,
                                                "kind": kind, "receiver": actor.get_full_name() or actor.username,
                                                "received_at": payment.created_at.isoformat(), "fiscal": False})
    return payment


@transaction.atomic
def begin_preparation(actor, order_id):
    order = _lock(order_id)
    _store(actor, order)
    if order.preparation_started_at:
        return order
    _state(order, Order.Status.APPROVED)
    quote = _ready_to_start(order)
    order.preparation_started_at = timezone.now()
    order.status = Order.Status.PREPARING
    eta = order.preparation_started_at + timedelta(minutes=quote.snapshot["estimated_delivery_minutes"])
    return _event(actor, order, "order.preparation_started", {"eta": eta.isoformat()})


@transaction.atomic
def create_delivery(actor, order_id, items, eta=None):
    order = _lock(order_id)
    _store(actor, order)
    _state(order, Order.Status.PREPARING, Order.Status.DELIVERING)
    if not items:
        raise ValidationError("Yetkazish tarkibi bo‘sh bo‘lmasin.")
    if eta is None:
        from apps.common.routing import travel_minutes
        eta = timezone.now() + timedelta(minutes=order.preparation_minutes + travel_minutes(order.store.store_profile, order))
    delivery = Delivery.objects.create(order=order, eta=eta)
    seen = set()
    for item in items:
        item_id = item["item_id"]
        if item_id in seen:
            raise ValidationError("Material yetkazishga bir marta kiritilsin.")
        seen.add(item_id)
        row = get_object_or_404(MaterialItem, pk=item_id, order=order)
        allocated = row.delivery_items.aggregate(total=Sum("quantity"))["total"] or ZERO
        count = quantity(item["quantity"])
        if allocated + count > row.quantity:
            raise ValidationError("Yetkazish miqdori tasdiqlangan material miqdoridan oshmasin.")
        DeliveryItem.objects.create(delivery=delivery, item=row, quantity=count)
    _event(actor, order, "order.delivery_created", {"delivery_id": delivery.pk, "eta": eta.isoformat() if eta else None})
    return delivery


@transaction.atomic
def update_delivery(actor, order_id, delivery_id, status, eta=None):
    order = _lock(order_id)
    _store(actor, order)
    _state(order, Order.Status.PREPARING, Order.Status.DELIVERING, Order.Status.DELIVERED, Order.Status.WORKING)
    delivery = get_object_or_404(Delivery, pk=delivery_id, order=order)
    transitions = {Delivery.Status.PREPARING: Delivery.Status.DISPATCHED, Delivery.Status.DISPATCHED: Delivery.Status.DELIVERED}
    if status == delivery.status and (eta is None or eta == delivery.eta):
        return delivery
    if status != delivery.status and transitions.get(delivery.status) != status:
        raise ValidationError("Yetkazish holati ketma-ket o‘zgarishi kerak.")
    if delivery.status == Delivery.Status.CONFIRMED:
        raise ValidationError("Mijoz tasdiqlagan yetkazishni o‘zgartirib bo‘lmaydi.")
    delivery.status = status
    if eta is not None:
        delivery.eta = eta
    delivery.save()
    if order.status != Order.Status.WORKING:
        order.status = Order.Status.DELIVERING
    _event(actor, order, "order.delivery_updated", {"delivery_id": delivery.pk, "status": status,
                                                   "eta": delivery.eta.isoformat() if delivery.eta else None})
    return delivery


@transaction.atomic
def confirm_delivery(actor, order_id, delivery_id):
    order = _lock(order_id)
    _customer(actor, order)
    if order.status in TERMINAL | {Order.Status.DISPUTED}:
        raise ValidationError("Hozir material qabulini tasdiqlab bo‘lmaydi.")
    delivery = get_object_or_404(Delivery, pk=delivery_id, order=order)
    if delivery.status == Delivery.Status.CONFIRMED:
        return delivery
    if delivery.status != Delivery.Status.DELIVERED:
        raise ValidationError("Do‘kon avval yetkazildi deb belgilashi kerak.")
    delivery.status = Delivery.Status.CONFIRMED
    delivery.confirmed_at = timezone.now()
    delivery.save()
    if _materials_received(order) and order.status != Order.Status.WORKING:
        order.status = Order.Status.DELIVERED
    _event(actor, order, "order.delivery_confirmed", {"delivery_id": delivery.pk})
    return delivery


def _materials_received(order):
    for row in order.material_items.all():
        received = row.delivery_items.filter(delivery__status=Delivery.Status.CONFIRMED).aggregate(total=Sum("quantity"))["total"] or ZERO
        if received != row.quantity:
            return False
    return True


@transaction.atomic
def report_issue(actor, order_id, description):
    order = _lock(order_id)
    _customer(actor, order)
    if order.status in TERMINAL | {Order.Status.DISPUTED} or not order.approved_version:
        raise ValidationError("Bu bosqichda nizo ochib bo‘lmaydi.")
    if not description.strip():
        raise ValidationError("Muammoni yozing.")
    issue = Issue.objects.create(order=order, opened_by=actor, description=description, previous_status=order.status)
    order.status = Order.Status.DISPUTED
    _event(actor, order, "order.dispute_opened", {"issue_id": issue.pk, "description": description})
    from apps.tg_bot.services import enqueue
    if order.store:
        enqueue(order.store, "order.dispute_opened", order, payload={"issue_id": issue.pk})
    return issue


@transaction.atomic
def schedule_work(actor, order_id, starts_at, ends_at, reason=""):
    order = _lock(order_id)
    _plumber(actor, order)
    if order.status in TERMINAL | {Order.Status.DISPUTED, Order.Status.COMPLETED, Order.Status.CUSTOMER_ACCEPTED, Order.Status.REJECTED}:
        raise ValidationError("Bu holatda ish jadvalini o‘zgartirib bo‘lmaydi.")
    if ends_at <= starts_at:
        raise ValidationError("Ish tugashi boshlanishidan keyin bo‘lsin.")
    if order.work_starts_at and not reason.strip():
        raise ValidationError("Jadval o‘zgarishining sababi kerak.")
    order.work_starts_at, order.work_ends_at = starts_at, ends_at
    return _event(actor, order, "order.schedule_updated", {"starts_at": starts_at.isoformat(), "ends_at": ends_at.isoformat(), "reason": reason})


@transaction.atomic
def start_work(actor, order_id):
    order = _lock(order_id)
    _plumber(actor, order)
    if order.status == Order.Status.WORKING:
        return order
    _state(order, Order.Status.APPROVED, Order.Status.PREPARING, Order.Status.DELIVERING, Order.Status.DELIVERED)
    _ready_to_start(order)
    if not _materials_received(order):
        raise ValidationError("Materiallar mijoz tomonidan to‘liq qabul qilinishi kerak.")
    order.work_started_at = timezone.now()
    order.status = Order.Status.WORKING
    return _event(actor, order, "order.work_started")


@transaction.atomic
def complete_work(actor, order_id):
    order = _lock(order_id)
    _plumber(actor, order)
    if order.status == Order.Status.COMPLETED:
        return order
    _state(order, Order.Status.WORKING)
    order.status = Order.Status.COMPLETED
    return _event(actor, order, "order.work_completed")


@transaction.atomic
def accept_work(actor, order_id):
    order = _lock(order_id)
    _customer(actor, order)
    if order.status in {Order.Status.CUSTOMER_ACCEPTED, Order.Status.CLOSED} and order.customer_accepted_at:
        return order
    _state(order, Order.Status.COMPLETED)
    order.customer_accepted_at = timezone.now()
    order.status = Order.Status.CLOSED if financial_summary(order)["balance_due"] == 0 else Order.Status.CUSTOMER_ACCEPTED
    return _event(actor, order, "order.work_accepted")


@transaction.atomic
def resolve_dispute(actor, order_id, note, accept_work=True):
    _staff(actor)
    order = _lock(order_id)
    _state(order, Order.Status.DISPUTED)
    if not note.strip():
        raise ValidationError("Nizo qarori haqida izoh kerak.")
    issue = order.issues.filter(resolved_at__isnull=True).order_by("-pk").first()
    if not issue:
        raise ValidationError("Ochiq nizo topilmadi.")
    issue.resolution, issue.resolved_at, issue.resolved_by = note, timezone.now(), actor
    issue.save()
    if accept_work:
        if issue.previous_status not in {Order.Status.COMPLETED, Order.Status.CUSTOMER_ACCEPTED}:
            raise ValidationError("Ish hali tugamagan; nizoni ishni qabul qilishsiz yoping.")
        order.customer_accepted_at = timezone.now()
        order.status = Order.Status.CLOSED if financial_summary(order)["balance_due"] == 0 else Order.Status.CUSTOMER_ACCEPTED
    else:
        order.status = issue.previous_status
    return _event(actor, order, "order.dispute_resolved", {"issue_id": issue.pk, "note": note, "accept_work": accept_work})


@transaction.atomic
def cancel_order(actor, order_id, reason="", company_failure=False):
    order = _lock(order_id)
    if not actor.is_staff:
        _customer(actor, order)
        if company_failure:
            raise PermissionDenied("Kompaniya sababini faqat admin belgilaydi.")
    if order.status == Order.Status.CANCELLED:
        if actor.is_staff and company_failure and not order.company_failure:
            if not reason.strip():
                raise ValidationError("Kompaniya sababli qaytarish qaroriga izoh zarur.")
            order.company_failure = True
            return _event(actor, order, "order.refund_authorized", {"reason": reason})
        return order
    if order.status in {Order.Status.CLOSED, Order.Status.CUSTOMER_ACCEPTED, Order.Status.COMPLETED, Order.Status.DISPUTED} and not actor.is_staff:
        raise ValidationError("Bu bosqichda xizmat markaziga murojaat qiling.")
    if order.status == Order.Status.CLOSED or order.settlements.exists():
        raise ValidationError("Hisob-kitob qilingan buyurtmani bekor qilib bo‘lmaydi.")
    if order.status == Order.Status.REJECTED and not actor.is_staff:
        raise PermissionDenied("Rad etilgan smetani admin yopadi yoki qayta tayinlaydi.")
    order.company_failure = bool(company_failure)
    if company_failure and not reason.strip():
        raise ValidationError("Kompaniya sababli bekor qilishga izoh zarur.")
    if not order.preparation_started_at and not order.work_started_at:
        # refund_limit is a cumulative ceiling, including prior repricing refunds.
        order.refund_limit = financial_summary(order)["paid"]
    order.status = Order.Status.CANCELLED
    return _event(actor, order, "order.cancelled", {"reason": reason, "company_failure": company_failure, "refund_limit": str(order.refund_limit)})


@transaction.atomic
def record_refund(actor, order_id, amount, reason, idempotency_key):
    _staff(actor)
    order = _lock(order_id)
    amount = money(amount, positive=True)
    existing = _idempotent(Refund, idempotency_key, order, {"amount": amount, "reason": reason, "recorded_by_id": actor.pk})
    if existing:
        return existing
    _state(order, Order.Status.CANCELLED, Order.Status.QUOTED, Order.Status.APPROVED, Order.Status.REJECTED)
    if not reason.strip():
        raise ValidationError("Qaytarish sababi zarur.")
    summary = financial_summary(order)
    if amount > summary["net_paid"]:
        raise ValidationError("Qaytarish olingan to‘lovdan oshmasin.")
    if order.status == Order.Status.CANCELLED:
        if not order.company_failure and summary["refunded"] + amount > order.refund_limit:
            raise ValidationError("Tayyorlash yoki ish boshlanganidan keyin avans qaytarilmaydi.")
    else:
        if order.preparation_started_at or order.work_started_at:
            raise ValidationError("Tayyorlash yoki ish boshlanganidan keyin qaytarish uchun bekor qilish qarori kerak.")
        quote = _current_quote(order)
        if order.status != Order.Status.REJECTED and amount > max(summary["net_paid"] - quote.advance_required, ZERO):
            raise ValidationError("Faqat qayta baholashdagi ortiqcha avans qaytariladi.")
    refund = _create_journal(Refund, order=order, amount=amount, reason=reason, recorded_by=actor, idempotency_key=idempotency_key)
    _event(actor, order, "order.refund_recorded", {"refund_id": refund.pk, "amount": str(amount), "reason": reason})
    return refund


@transaction.atomic
def confirm_cash_handover(actor, order_id, payment_id):
    _staff(actor)
    order = _lock(order_id)
    payment = get_object_or_404(Payment.objects.select_related("received_by"), pk=payment_id, order=order)
    if payment.method != "cash" or payment.received_by.is_staff or payment.received_by.role != User.Role.PLUMBER:
        raise ValidationError("Faqat santexnik olgan naqd pul topshiriladi.")
    handover, created = CashHandover.objects.get_or_create(payment=payment, defaults={"confirmed_by": actor})
    if created:
        _event(actor, order, "order.cash_handover", {"payment_id": payment.pk, "amount": str(payment.amount)})
    return handover


@transaction.atomic
def record_settlement(actor, order_id, partner, amount, idempotency_key):
    _staff(actor)
    order = _lock(order_id)
    amount = money(amount, positive=True)
    if partner not in {"store", "plumber"}:
        raise ValidationError("Hamkor turi noto‘g‘ri.")
    existing = _idempotent(Settlement, idempotency_key, order, {"amount": amount, "partner": partner, "recorded_by_id": actor.pk})
    if existing:
        return existing
    _state(order, Order.Status.CLOSED)
    summary = financial_summary(order)
    if not order.customer_accepted_at or summary["balance_due"] or order.issues.filter(resolved_at__isnull=True).exists():
        raise ValidationError("Mijoz tasdig‘i, to‘liq to‘lov va yopilgan nizolar talab etiladi.")
    if order.payments.filter(method="cash", received_by__is_staff=False, handover__isnull=True).exists():
        raise ValidationError("Santexnikdagi naqd pul avval markazga topshirilsin.")
    if amount > summary[f"{partner}_due"]:
        raise ValidationError("Hisob-kitob hamkor sof qarzdorligidan oshmasin.")
    settlement = _create_journal(Settlement, order=order, partner=partner, amount=amount, recorded_by=actor, idempotency_key=idempotency_key)
    _event(actor, order, "order.settlement_recorded", {"settlement_id": settlement.pk, "partner": partner, "amount": str(amount)}, notify=False)
    from apps.tg_bot.services import enqueue
    enqueue(order.store if partner == "store" else order.plumber, "order.settlement_recorded", order, payload={"amount": str(amount)})
    return settlement


@transaction.atomic
def rate_order(actor, order_id, plumber_score, store_score, comment=""):
    order = _lock(order_id)
    _customer(actor, order)
    _state(order, Order.Status.CLOSED)
    if not (1 <= plumber_score <= 5 and 1 <= store_score <= 5):
        raise ValidationError("Baho 1 dan 5 gacha bo‘lsin.")
    if Rating.objects.filter(order=order).exists():
        raise ValidationError("Buyurtma avval baholangan.")
    rating = Rating.objects.create(order=order, plumber_score=plumber_score, store_score=store_score, comment=comment)
    _event(actor, order, "order.rating_submitted", {"rating_id": rating.pk}, notify=False)
    return rating


@transaction.atomic
def moderate_rating(actor, order_id, rating_id, approved):
    _staff(actor)
    order = _lock(order_id)
    rating = get_object_or_404(Rating, pk=rating_id, order=order)
    rating.approved, rating.moderated_at, rating.moderated_by = bool(approved), timezone.now(), actor
    rating.save()
    _event(actor, order, "order.rating_moderated", {"rating_id": rating.pk, "approved": bool(approved)}, notify=False)
    return rating


@transaction.atomic
def add_attachment(actor, order_id, file, purpose):
    order = _lock(order_id)
    if purpose == "request":
        _customer(actor, order)
        _state(order, Order.Status.REQUESTED, Order.Status.ASSIGNED, Order.Status.ACCEPTED, Order.Status.INSPECTION)
    elif purpose == "completion":
        _plumber(actor, order)
        _state(order, Order.Status.WORKING, Order.Status.COMPLETED)
    elif purpose == "issue":
        _customer(actor, order)
        _state(order, Order.Status.DISPUTED)
    else:
        raise ValidationError("Fayl maqsadi noto‘g‘ri.")
    allowed = {"image/jpeg": "jpg", "image/png": "png", "image/webp": "webp", "video/mp4": "mp4", "video/quicktime": "mov"}
    content_type = getattr(file, "content_type", "")
    from django.conf import settings
    if file.size <= 0 or file.size > settings.MAX_ORDER_MEDIA_BYTES or content_type not in allowed:
        raise ValidationError("Faqat JPEG/PNG/WebP yoki MP4/MOV, 20 MB gacha.")
    header = file.read(32)
    file.seek(0)
    signatures = {"image/jpeg": header.startswith(b"\xff\xd8\xff"), "image/png": header.startswith(b"\x89PNG\r\n\x1a\n"),
        "image/webp": header.startswith(b"RIFF") and header[8:12] == b"WEBP",
        "video/mp4": header[4:8] == b"ftyp" and header[8:12] not in {b"qt  "},
        "video/quicktime": header[4:8] == b"ftyp" and header[8:12] == b"qt  "}
    if not signatures[content_type]:
        raise ValidationError("Fayl tarkibi uning turiga mos kelmaydi.")
    file.name = "upload." + allowed[content_type]
    attachment = Attachment.objects.create(order=order, uploaded_by=actor, file=file, purpose=purpose)
    _event(actor, order, "order.attachment_added", {"attachment_id": attachment.pk}, notify=False)
    return attachment
