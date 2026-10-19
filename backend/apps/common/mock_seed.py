"""Explicit, development-only fixture factory for the complete domain graph.

Snapshots are inserted once, never rewritten. This deliberately does not replay
application services: their outbox fan-out could notify existing staff accounts.
All inserted domain instances pass full_clean(), and no DB guards are disabled.
"""
from collections import defaultdict
from datetime import time, timedelta
from decimal import Decimal, ROUND_HALF_UP
from hashlib import sha256
from io import BytesIO
import logging
import re

from django.apps import apps
from django.conf import settings
from django.core.files.base import ContentFile
from django.db import connection, transaction
from django.db.models import Max
from django.utils import timezone
from PIL import Image, ImageDraw

from apps.catalog.models import ContractTemplate, Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.common.audit import AuditEvent
from apps.orders.models import (
    Attachment, CashHandover, Contract, Delivery, DeliveryItem, Issue, MaterialItem,
    Order, OrderEvent, Payment, Quote, Rating, Refund, ServiceItem, Settlement,
)
from apps.users.models import Consumer, PlumberProfile, Store, User
from apps.tg_bot.models import BotUpdate, Notification


APP_LABELS = ("common", "catalog", "users", "orders", "tg_bot")
SCHEMA_VERSION = 1
MANIFEST_ACTION = "mock.seed.completed"
PREVIEW_USERNAME = "__santex_local_preview__"
CENT = Decimal("0.01")
LOGGER = logging.getLogger(__name__)

NAMES = (
    "Ali", "Vali", "Aziz", "Dilshod", "Sardor", "Javohir", "Bekzod", "Akmal", "Jasur", "Bobur",
    "Malika", "Madina", "Dilnoza", "Shahnoza", "Nodira", "Sevara", "Zarina", "Kamola", "Umida", "Gulnoza",
)
REGIONS = (
    "Marhamat", "Andijon", "Asaka", "Baliqchi", "Bo‘ston", "Buloqboshi", "Izboskan", "Jalaquduq",
    "Xo‘jaobod", "Oltinko‘l", "Paxtaobod", "Qo‘rg‘ontepa", "Shahrixon", "Ulug‘nor", "Xonobod",
    "Namangan", "Chust", "Kosonsoy", "Farg‘ona", "Marg‘ilon",
)
# Group, service, unit, material: realistic labels, explicitly marked as mock.
CATALOG = (
    ("Kran ta’miri", "Aralashtirgichni ta’mirlash", "dona", "Kran kartriji"),
    ("Kran o‘rnatish", "Yangi aralashtirgich o‘rnatish", "dona", "Aralashtirgich"),
    ("Rakovo‘na", "Rakovo‘na o‘rnatish", "dona", "Rakovo‘na sifoni"),
    ("Unitaz", "Unitaz o‘rnatish", "dona", "Unitaz manjeti"),
    ("Dush", "Dush to‘plamini almashtirish", "dona", "Dush shlangi"),
    ("Quvur", "PPR quvur ulash", "metr", "PPR quvur"),
    ("Kanalizatsiya", "Kanalizatsiya quvurini almashtirish", "metr", "PVC quvur"),
    ("Tiqilish", "Suv yo‘lini tozalash", "dona", "Quvur tozalash vositasi"),
    ("Radiator", "Radiator o‘rnatish", "dona", "Radiator klapani"),
    ("Isitish", "Isitish tizimini sozlash", "dona", "Termostat"),
    ("Boyler", "Boyler ulash", "dona", "Xavfsizlik klapani"),
    ("Nasos", "Suv nasosini almashtirish", "dona", "Nasos ulash muftasi"),
    ("Hisoblagich", "Suv hisoblagichini o‘rnatish", "dona", "Hisoblagich prokladkasi"),
    ("Filtr", "Suv filtrini o‘rnatish", "dona", "Filtr kartriji"),
    ("Sifon", "Sifonni almashtirish", "dona", "Sifon to‘plami"),
    ("Ventil", "Suv ventilini almashtirish", "dona", "Sharli ventil"),
    ("Kir yuvish mashinasi", "Mashina suv yo‘lini ulash", "dona", "Ulash shlangi"),
    ("Vanna", "Vanna suv chiqarishini ulash", "dona", "Vanna sifoni"),
    ("Suv sizishi", "Suv sizishini bartaraf etish", "dona", "Germetik lenta"),
    ("Profilaktika", "Santexnika tekshiruvi", "dona", "Muhrlash to‘plami"),
)
TEMPLATE_TEXT = {
    "uz": "MOCK — FAQAT SINOV UCHUN. Bu yuridik shartnoma emas. Namuna: ishlar smeta bo‘yicha, materiallar qabul bilan, yakun mijoz tasdig‘i bilan qayd etiladi.",
    "ru": "MOCK — ТОЛЬКО ДЛЯ ТЕСТА. Не является юридическим договором. Пример: работы по смете, приёмка материалов и подтверждение заказчика.",
    "en": "MOCK — TEST DATA ONLY. This is not a legal agreement. Example: quoted work, material receipt and customer acceptance are recorded.",
}


def domain_models():
    return {model._meta.label: model for label in APP_LABELS for model in apps.get_app_config(label).get_models()
            if not model._meta.proxy and model._meta.managed}


def ensure_development():
    module = getattr(settings, "SETTINGS_MODULE", "")
    if module == "project_backend.settings.production" or not (settings.DEBUG or module == "project_backend.settings.test"):
        raise ValueError("seed_mock faqat development/test uchun. Production bazasida mock moliya va shartnoma yaratilmaydi.")


def validate_existing(manifest, count, local_preview):
    payload = manifest.payload
    if (payload.get("schema_version"), payload.get("count"), payload.get("local_preview")) != (SCHEMA_VERSION, count, local_preview):
        raise ValueError("Bu prefix boshqa count/rejim/seed versiyasi bilan ishlatilgan. Yangi --prefix tanlang.")
    records = payload.get("records", {})
    models = domain_models()
    if set(records) != set(models):
        raise ValueError("Modellar ro‘yxati o‘zgargan. Seedni yangilab yangi --prefix ishlating.")
    for label, ids in records.items():
        minimum = 1 if models[label] is ServiceCenter else count
        if len(ids) < minimum or models[label].objects.filter(pk__in=ids, is_deleted=False).count() != len(ids):
            raise ValueError(f"{label} uchun batch yozuvlari yetishmaydi yoki arxivlangan. Mavjud tarix o‘zgartirilmaydi; yangi --prefix ishlating.")
    for model, field_name in ((Attachment, "file"), (PlumberProfile, "photo")):
        for instance in model.objects.filter(pk__in=records[model._meta.label]):
            field = getattr(instance, field_name)
            if not field.name or not field.storage.exists(field.name):
                raise ValueError("Batchning mock fayli o‘chirilgan. Mavjud tarix o‘zgartirilmaydi; yangi --prefix ishlating.")
    return {"reused": True, "records": records}


def seed_mock_data(*, count=20, prefix="mock", local_preview=True):
    ensure_development()
    if type(count) is not int or not 1 <= count <= 200:
        raise ValueError("--count 1 dan 200 gacha bo‘lishi kerak.")
    if not re.fullmatch(r"[a-z](?:[a-z0-9-]{0,22}[a-z0-9])?", prefix):
        raise ValueError("--prefix: 1–24 ta kichik lotin harfi/raqam/defis; harf bilan boshlansin.")
    seeder = MockSeeder(count, prefix, local_preview)
    try:
        with transaction.atomic():
            if connection.vendor == "postgresql":
                # Serialize even different prefixes: template versions and the singleton are shared.
                lock_id = int.from_bytes(sha256(b"santex:seed_mock").digest()[:8], "big", signed=True)
                with connection.cursor() as cursor:
                    cursor.execute("SELECT pg_advisory_xact_lock(%s)", [lock_id])
            manifest = AuditEvent.objects.filter(action=MANIFEST_ACTION, object_type="mock.batch", object_id=prefix).first()
            if manifest:
                return validate_existing(manifest, count, local_preview)
            seeder.run()
            records = dict(seeder.records)
            # The immutable audit row is the completion marker; a failed batch has no marker.
            manifest = AuditEvent(action=MANIFEST_ACTION, object_type="mock.batch", object_id=prefix, payload={
                "schema_version": SCHEMA_VERSION, "count": count, "local_preview": local_preview,
                "records": records,
            })
            manifest.full_clean()
            manifest.save()
        return {"reused": False, "records": records}
    except BaseException:
        # File storage is outside the DB transaction. Delete only files made by THIS attempt.
        seeder.cleanup_files()
        raise


class MockSeeder:
    def __init__(self, count, prefix, local_preview):
        self.count = count
        self.prefix = prefix
        self.local_preview = local_preview
        self.records = defaultdict(list)
        self.record_ids = defaultdict(set)
        self.files = []
        self.templates = defaultdict(list)

    def remember(self, instance):
        label = instance._meta.label
        ids = self.record_ids[label]
        if instance.pk not in ids:
            ids.add(instance.pk)
            self.records[label].append(instance.pk)
        return instance

    def create(self, model, **values):
        instance = model(**values)
        instance.full_clean()
        instance.save()
        return self.remember(instance)

    def cleanup_files(self):
        for storage, name in reversed(self.files):
            try:
                storage.delete(name)
            except Exception:
                LOGGER.warning("Mock seed faylini tozalab bo‘lmadi: %s", name)

    def image(self, field, name, index):
        image = Image.new("RGB", (240, 160), "#e7f4fb")
        draw = ImageDraw.Draw(image)
        draw.line([(40, 110), (110, 110), (110, 55), (190, 55)], fill="#087eb2", width=18)
        draw.text((16, 14), f"MOCK {index:03d} - {self.prefix}", fill="#12364c")
        content = BytesIO()
        image.save(content, format="PNG")
        saved = field.storage.save(f"mock/{self.prefix}/{name}-{index:03d}.png", ContentFile(content.getvalue()))
        self.files.append((field.storage, saved))
        field.name = saved

    def user(self, index, role, *, staff=False):
        username = f"{self.prefix}-{role}-{index:03d}" if not staff else f"{self.prefix}-staff"
        preview = self.local_preview and role == User.Role.CUSTOMER and index == 1 and not staff
        if preview:
            username = PREVIEW_USERNAME
            existing = User.objects.filter(username=username).first()
            if existing:
                if (existing.role != User.Role.CUSTOMER or existing.is_staff or existing.is_superuser
                        or existing.telegram_id is not None or existing.has_usable_password() or not existing.is_active
                        or existing.is_deleted or existing.email != "local-preview@invalid.example"
                        or existing.phone_number != "+998000000000" or not existing.phone_verified_at):
                    raise ValueError("Reserved preview akkaunti kutilgan dev akkaunti emas; unga tegilmadi. --no-local-preview ishlating.")
                return self.remember(existing)
        # A collision with a pre-existing account is an error, never an overwrite.
        if User.objects.filter(username=username).exists():
            raise ValueError(f"{username} mavjud, lekin bu batch yakunlanmagan. Boshqa --prefix tanlang.")
        person = User(username=username, role=role, is_staff=staff, is_superuser=False,
                      first_name="MOCK" if staff else NAMES[(index - 1) % len(NAMES)], last_name="Sinov",
                      email="local-preview@invalid.example" if preview else f"{username}@example.invalid",
                      phone_number="+998000000000" if preview else f"+998000{(index + (1000 if role == User.Role.PLUMBER else 2000 if role == User.Role.STORE else 0)):06d}",
                      phone_verified_at=timezone.now(), language=("uz", "ru", "en")[(index - 1) % 3])
        person.set_unusable_password()
        person.full_clean()
        person.save()
        return self.remember(person)

    def center(self):
        center = ServiceCenter.objects.filter(pk=1).first()
        if center:
            if center.is_deleted:
                raise ValueError("Xizmat markazi arxivlangan. Mock seed uni qayta ochmaydi.")
            return self.remember(center)
        return self.create(ServiceCenter, pk=1, name=f"MOCK {self.prefix} xizmat markazi",
                           address="Sinov ko‘chasi, 1-uy (namuna)", phone="+998000000000",
                           opening_time=time(8), closing_time=time(20), working_days=list(range(7)),
                           default_plumber_commission=Decimal("10"), default_store_commission=Decimal("5"),
                           advance_kind="percent", advance_value=Decimal("50"), plumber_response_minutes=15)

    def event(self, order, actor, action, *, status=None, **payload):
        if status:
            order.status = status
        order.full_clean()
        order.save()
        payload = {"mock_seed": self.prefix, **payload}
        self.create(OrderEvent, order=order, actor=actor, action=action, status=order.status, payload=payload)
        self.create(AuditEvent, actor=actor, action=action, object_type=order._meta.label_lower,
                    object_id=str(order.pk), payload=payload)

    def run(self):
        self.service_center = self.center()
        # At least one test template for each supported language, including --count 1/2.
        versions = {language: ContractTemplate.objects.filter(language=language).aggregate(value=Max("version"))["value"] or 0
                    for language in TEMPLATE_TEXT}
        for index in range(max(3, self.count)):
            language = ("uz", "ru", "en")[index % 3]
            versions[language] += 1
            template = self.create(ContractTemplate, language=language, version=versions[language],
                                   text=f"[{self.prefix}] {TEMPLATE_TEXT[language]}")
            self.templates[language].append(template)
        self.staff = self.user(1, User.Role.CUSTOMER, staff=True)
        self.remember(Consumer.objects.get(user=self.staff))
        rows = []
        for index in range(1, self.count + 1):
            group_name, service_name, unit, material_name = CATALOG[(index - 1) % len(CATALOG)]
            region = self.create(Region, name=f"MOCK {REGIONS[(index - 1) % len(REGIONS)]} {index:02d}",
                                 code=f"{self.prefix}-region-{index:03d}")
            group = self.create(ServiceGroup, name=f"MOCK {group_name}", name_ru=f"MOCK Услуга {index}",
                                name_en=f"MOCK Service group {index}", code=f"{self.prefix}-group-{index:03d}")
            service = self.create(Service, group=group, name=f"MOCK {service_name}", name_ru=f"MOCK Сантехническая работа {index}",
                                  name_en=f"MOCK Plumbing work {index}", unit=unit, warranty_days=30 + index * 3)
            rate = self.create(ServiceRate, region=region, service=service,
                               unit_price=Decimal(80000 + index * 5000), urgent_fee=Decimal("25000"))
            material = self.create(Material, name=f"MOCK {material_name}", unit="dona", brand=f"MockBrand {index:02d}")
            customer = self.user(index, User.Role.CUSTOMER)
            # New users receive a profile from post_save; repair a missing preview profile only.
            consumer, _ = Consumer.objects.get_or_create(user=customer)
            if consumer.is_deleted:
                raise ValueError("Preview mijoz profili arxivlangan; --no-local-preview ishlating.")
            if not consumer.address:
                consumer.address = f"MOCK {region.name}, Sinov ko‘chasi, {index}-uy"
                if consumer.latitude is None and consumer.longitude is None:
                    consumer.latitude, consumer.longitude = Decimal("40.500000"), Decimal("72.300000")
                consumer.save()
            self.remember(consumer)
            plumber = self.user(index, User.Role.PLUMBER)
            profile = PlumberProfile(user=plumber, commission_rate=Decimal("10"), experience_years=1 + index % 15)
            self.image(profile.photo, "plumber", index)
            profile.full_clean()
            profile.save()
            self.remember(profile)
            profile.regions.add(region)
            profile.services.add(group)
            store_user = self.user(index, User.Role.STORE)
            store = self.create(Store, user=store_user, name=f"MOCK Santex do‘koni {index:02d}",
                                address=f"Sinov bozori, {index}-rasta", latitude=Decimal("40.510000"),
                                longitude=Decimal("72.310000"), commission_rate=Decimal("5"))
            rows.append((customer, plumber, store, region, group, service, rate, material))
        # The browser's local-preview customer can see the complete sample order list.
        for index, row in enumerate(rows, 1):
            customer, plumber, store, region, group, service, rate, material = row
            if self.local_preview:
                customer = rows[0][0]
            self.order(index, customer, plumber, store, region, group, service, rate, material)
        for label, model in domain_models().items():
            minimum = 1 if model is ServiceCenter else self.count
            if len(self.records[label]) < minimum:
                raise RuntimeError(f"{label} mock factory bilan qoplanmagan. Batch bekor qilindi.")

    def quote(self, order, service_item, material_item, version, material_price):
        service_total = (service_item.quantity * service_item.unit_price).quantize(CENT, ROUND_HALF_UP)
        material_total = (material_item.quantity * material_price).quantize(CENT, ROUND_HALF_UP)
        total = service_total + material_total + order.delivery_fee
        advance = (total / 2).quantize(CENT, ROUND_HALF_UP)
        plumber_commission = (service_total * Decimal("0.10")).quantize(CENT, ROUND_HALF_UP)
        store_commission = (material_total * Decimal("0.05")).quantize(CENT, ROUND_HALF_UP)
        snapshot = {
            "services": [{"id": service_item.pk, "service_id": service_item.service_id, "name": service_item.name,
                          "unit": service_item.unit, "quantity": str(service_item.quantity), "unit_price": str(service_item.unit_price),
                          "warranty_days": service_item.warranty_days, "subtotal": str(service_total)}],
            "materials": [{"id": material_item.pk, "material_id": material_item.material_id, "name": material_item.name,
                           "original_name": material_item.name, "unit": material_item.unit, "quantity": str(material_item.quantity),
                           "brand": material_item.brand, "unit_price": str(material_price), "available": True,
                           "supply_minutes": 0, "subtotal": str(material_total)}],
            "currency": "UZS", "vat_included": True, "service_total": str(service_total), "material_total": str(material_total),
            "delivery_fee": str(order.delivery_fee), "urgent_fee": "0.00", "platform_fee": "0.00",
            "total": str(total), "advance_required": str(advance), "plumber_rate": "10.00", "store_rate": "5.00",
            "plumber_commission": str(plumber_commission), "store_commission": str(store_commission),
            "plumber_net": str(service_total - plumber_commission),
            "store_net": str(material_total + order.delivery_fee - store_commission),
            "preparation_minutes": 15, "travel_minutes": 10, "estimated_delivery_minutes": 25,
            "mock_seed": self.prefix,
        }
        return self.create(Quote, order=order, version=version, snapshot=snapshot, total=total, advance_required=advance)

    def contract(self, order, quote, index):
        language = order.customer.language
        templates = self.templates[language]
        template = templates[(index - 1) % len(templates)]
        contract = self.create(Contract, order=order, quote=quote, language=language, template_version=template.version,
                               text_snapshot=template.text, signed_at=timezone.now(), signed_by=self.staff,
                               parties_snapshot={"customer_id": order.customer_id, "customer": order.customer.get_full_name(),
                                                 "plumber_id": order.plumber_id, "plumber": order.plumber.get_full_name(),
                                                 "store_id": order.store_id, "store": order.store.store_profile.name,
                                                 "center": self.service_center.name, "address": order.address,
                                                 "phone": order.phone_snapshot, "work_starts_at": order.work_starts_at.isoformat(),
                                                 "work_ends_at": order.work_ends_at.isoformat(), "mock_seed": self.prefix})
        order.approved_version = quote.version
        self.event(order, order.customer, "order.quote_approved", status=Order.Status.APPROVED, quote_version=quote.version)
        self.event(order, self.staff, "order.contract_signed", contract_id=contract.pk)

    def order(self, index, customer, plumber, store, region, group, service, rate, material):
        order = self.create(Order, customer=customer, region=region, service_group=group,
                            address=f"MOCK {region.name}, Namunaviy ko‘cha, {index}-uy",
                            latitude=Decimal("40.500000") + Decimal(index) / 100000,
                            longitude=Decimal("72.300000") + Decimal(index) / 100000,
                            description=f"[{self.prefix}] MOCK: {service.name}. Ko‘rgazmali buyurtma {index:03d}.",
                            consent_at=timezone.now(), phone_snapshot=customer.phone_number)
        self.event(order, customer, "order.created")
        order.plumber = plumber
        self.event(order, self.staff, "order.plumber_assigned", status=Order.Status.ASSIGNED)
        order.plumber_accepted = True
        self.event(order, plumber, "order.plumber_accepted", status=Order.Status.ACCEPTED)
        order.inspection_at = timezone.now()
        self.event(order, plumber, "order.inspection_scheduled", status=Order.Status.INSPECTION)
        service_item = self.create(ServiceItem, order=order, service=service, name=service.name, unit=service.unit,
                                   quantity=Decimal("1.000"), unit_price=rate.unit_price, urgent_fee=rate.urgent_fee,
                                   warranty_days=service.warranty_days)
        final_price = Decimal(30000 + index * 1500)
        material_item = self.create(MaterialItem, order=order, material=material, name=material.name, unit=material.unit,
                                    brand=material.brand, note="MOCK: namuna material", quantity=Decimal("2.000"),
                                    unit_price=final_price * 3, available=True)
        self.event(order, plumber, "order.estimate_submitted", status=Order.Status.ESTIMATE)
        order.store = store.user
        self.event(order, self.staff, "order.store_assigned", status=Order.Status.STORE_ASSIGNED)
        order.store_accepted = True
        self.event(order, store.user, "order.store_accepted", status=Order.Status.STORE_ACCEPTED)
        order.work_starts_at = timezone.now()
        order.work_ends_at = order.work_starts_at + timedelta(hours=2)
        order.delivery_fee = Decimal("20000.00")
        order.preparation_minutes = 15
        first_quote = self.quote(order, service_item, material_item, 1, final_price * 3)
        order.quote_version = 1
        self.event(order, store.user, "order.quote_published", status=Order.Status.QUOTED, quote_version=1)
        self.contract(order, first_quote, index)
        payment = self.create(Payment, order=order, amount=first_quote.advance_required, method="cash", kind="advance",
                              received_by=plumber, idempotency_key=f"{self.prefix}-advance-{index:03d}")
        self.event(order, plumber, "order.payment_received", amount=str(payment.amount), payment_id=payment.pk)
        self.create(CashHandover, payment=payment, confirmed_by=self.staff)
        self.event(order, self.staff, "order.cash_handover", payment_id=payment.pk)
        # A second, cheaper quote creates a legitimate partial advance refund.
        material_item.unit_price = final_price
        material_item.full_clean()
        material_item.save()
        quote = self.quote(order, service_item, material_item, 2, final_price)
        order.quote_version, order.approved_version = 2, None
        self.event(order, store.user, "order.quote_published", status=Order.Status.QUOTED, quote_version=2)
        refund = self.create(Refund, order=order, amount=first_quote.advance_required - quote.advance_required,
                             reason="MOCK: material narxi kamaygach ortiqcha avans qaytarildi.", recorded_by=self.staff,
                             idempotency_key=f"{self.prefix}-refund-{index:03d}")
        self.event(order, self.staff, "order.refund_recorded", refund_id=refund.pk, amount=str(refund.amount))
        self.contract(order, quote, index)
        order.preparation_started_at = timezone.now()
        self.event(order, store.user, "order.preparation_started", status=Order.Status.PREPARING)
        delivery = self.create(Delivery, order=order, eta=timezone.now() + timedelta(minutes=25))
        self.create(DeliveryItem, delivery=delivery, item=material_item, quantity=material_item.quantity)
        self.event(order, store.user, "order.delivery_created", delivery_id=delivery.pk)
        for status in (Delivery.Status.DISPATCHED, Delivery.Status.DELIVERED):
            delivery.status = status
            delivery.save()
            self.event(order, store.user, "order.delivery_updated", status=Order.Status.DELIVERING, delivery_id=delivery.pk)
        delivery.status, delivery.confirmed_at = Delivery.Status.CONFIRMED, timezone.now()
        delivery.save()
        self.event(order, customer, "order.delivery_confirmed", status=Order.Status.DELIVERED, delivery_id=delivery.pk)
        order.work_started_at = timezone.now()
        self.event(order, plumber, "order.work_started", status=Order.Status.WORKING)
        attachment = Attachment(order=order, uploaded_by=plumber, purpose="completion")
        self.image(attachment.file, "completion", index)
        attachment.full_clean()
        attachment.save()
        self.remember(attachment)
        self.event(order, plumber, "order.attachment_added", attachment_id=attachment.pk)
        self.event(order, plumber, "order.work_completed", status=Order.Status.COMPLETED)
        issue = self.create(Issue, order=order, opened_by=customer, previous_status=Order.Status.COMPLETED,
                            description="MOCK: ulanishni yana bir marta tekshirish so‘raldi.")
        self.event(order, customer, "order.dispute_opened", status=Order.Status.DISPUTED, issue_id=issue.pk)
        issue.resolution, issue.resolved_at, issue.resolved_by = "MOCK: qayta tekshirildi, namuna nizo yopildi.", timezone.now(), self.staff
        issue.full_clean()
        issue.save()
        order.customer_accepted_at = timezone.now()
        self.event(order, self.staff, "order.dispute_resolved", status=Order.Status.CUSTOMER_ACCEPTED, issue_id=issue.pk, accept_work=True)
        balance = self.create(Payment, order=order, amount=quote.total - quote.advance_required, method="terminal", kind="balance",
                              received_by=self.staff, idempotency_key=f"{self.prefix}-balance-{index:03d}")
        self.event(order, self.staff, "order.payment_received", status=Order.Status.CLOSED, payment_id=balance.pk, amount=str(balance.amount))
        for partner in ("plumber", "store"):
            settlement = self.create(Settlement, order=order, partner=partner, amount=Decimal(quote.snapshot[f"{partner}_net"]),
                                     recorded_by=self.staff, idempotency_key=f"{self.prefix}-{partner}-settlement-{index:03d}")
            self.event(order, self.staff, "order.settlement_recorded", settlement_id=settlement.pk, partner=partner)
        rating = self.create(Rating, order=order, plumber_score=4 + index % 2, store_score=4 + (index + 1) % 2,
                             comment=f"MOCK: namuna xizmat bahosi {index:03d}.", approved=True,
                             moderated_at=timezone.now(), moderated_by=self.staff)
        self.event(order, customer, "order.rating_submitted", rating_id=rating.pk)
        self.event(order, self.staff, "order.rating_moderated", rating_id=rating.pk, approved=True)
        self.create(Notification, user=customer, event="order.work_accepted", order_id=order.pk,
                    payload={"mock_seed": self.prefix}, sent_at=timezone.now(), read_at=timezone.now())
        namespace = int.from_bytes(sha256(self.prefix.encode()).digest()[:6], "big")
        # Live Telegram update IDs are nonnegative; keep seed IDs in a disjoint range.
        self.create(BotUpdate, update_id=-(namespace * 1000 + index))
