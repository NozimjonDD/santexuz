"""HTTP-level business acceptance tests. Do not run on the write-only machine."""
from datetime import time, timedelta
from decimal import Decimal
from io import BytesIO
import tempfile
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.management import call_command
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.catalog.models import ContractTemplate, Material, Region, Service, ServiceCenter, ServiceGroup, ServiceRate
from apps.common.audit import AuditEvent
from apps.orders.models import Attachment, CashHandover, Contract, Order, Payment, Quote, Rating, Refund, Settlement
from apps.orders.selectors import financial_summary
from apps.tg_bot.models import Notification
from apps.users.models import PlumberProfile, Store, User


class WorkflowAPITests(APITestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="operator", is_staff=True, telegram_id=100)
        self.customer = User.objects.create_user(username="customer", first_name="Ali", telegram_id=101,
            phone_number="+998901234567", phone_verified_at=timezone.now())
        self.other = User.objects.create_user(username="other", telegram_id=102)
        self.plumber = User.objects.create_user(username="plumber", role="plumber", telegram_id=103, phone_number="+998901111111")
        self.store = User.objects.create_user(username="store", role="store", telegram_id=104, phone_number="+998902222222")
        self.region = Region.objects.create(code="test-marhamat", name="Marhamat")
        self.group = ServiceGroup.objects.create(code="repair", name="Ta’mirlash")
        self.service = Service.objects.create(group=self.group, name="Kran ta’miri", unit="dona", warranty_days=90)
        self.rate = ServiceRate.objects.create(region=self.region, service=self.service, unit_price="100000", urgent_fee="20000")
        self.material = Material.objects.create(name="Kran", unit="dona", brand="Test")
        self.plumber_profile = PlumberProfile.objects.create(user=self.plumber)
        self.plumber_profile.regions.add(self.region)
        self.plumber_profile.services.add(self.group)
        self.store_profile = Store.objects.create(user=self.store, name="Do‘kon", address="Test", latitude="40.5", longitude="72.3")
        self.center = ServiceCenter.objects.create(name="Markaz", address="Test", phone="+998903333333",
            opening_time=time(0, 0), closing_time=time(23, 59), working_days=list(range(7)),
            default_plumber_commission="10", default_store_commission="5", advance_kind="percent",
            advance_value="50", plumber_response_minutes=15)
        for language in ("uz", "ru", "en"):
            ContractTemplate.objects.create(language=language, version=1, text="Test fixture only; not a legal contract.")
        routing = patch("apps.common.routing.travel_minutes", return_value=20)
        routing.start()
        self.addCleanup(routing.stop)

    def request(self, user, method, path, data=None, expected=200):
        self.client.force_authenticate(user)
        response = getattr(self.client, method)(path, data or {}, format="json")
        self.assertEqual(response.status_code, expected, getattr(response, "data", None))
        return response

    def action(self, user, order, action, data=None, expected=200, staff=False):
        namespace = "admin" if staff else "site"
        return self.request(user, "post", f"/api/v1/{namespace}/orders/{order.pk}/{action}/", data, expected)

    def create_order(self, **extra):
        payload = {"region_id": self.region.pk, "service_group_id": self.group.pk,
                   "address": "Marhamat, test 1", "latitude": "40.500000", "longitude": "72.300000", "consent": True, **extra}
        response = self.request(self.customer, "post", "/api/v1/site/orders/", payload, 201)
        return Order.objects.get(pk=response.data["id"])

    def estimate(self, order):
        self.action(self.staff, order, "assign-plumber", {"plumber_id": self.plumber.pk}, staff=True)
        self.action(self.plumber, order, "plumber-response", {"accept": True})
        self.action(self.plumber, order, "inspection", {"inspection_at": (timezone.now() + timedelta(hours=1)).isoformat()})
        self.action(self.plumber, order, "estimate", {"services": [{"service_id": self.service.pk, "quantity": "2"}],
            "materials": [{"material_id": self.material.pk, "quantity": "4"}]})
        self.action(self.plumber, order, "work-schedule", {"starts_at": (timezone.now() + timedelta(days=1)).isoformat(),
            "ends_at": (timezone.now() + timedelta(days=1, hours=2)).isoformat()})
        self.action(self.staff, order, "assign-store", {"store_id": self.store.pk}, staff=True)
        self.action(self.store, order, "store-response", {"accept": True})
        return order.material_items.get()

    def price(self, order, item, price="10000", delivery_fee="10000"):
        response = self.action(self.store, order, "material-prices", {"items": [{"id": item.pk, "unit_price": price, "available": True}],
            "delivery_fee": delivery_fee, "preparation_minutes": 30})
        order.refresh_from_db()
        return response

    def quoted(self):
        order = self.create_order()
        item = self.estimate(order)
        self.price(order, item)
        return order, item

    def approved(self):
        order, item = self.quoted()
        self.action(self.customer, order, "approve-quote", {"quote_version": order.quote_version})
        self.action(self.staff, order, "sign-contract", staff=True)
        return order, item

    def paid_advance(self, order, receiver=None, key="advance-1"):
        return self.action(receiver or self.staff, order, "payments", {"amount": str(order.quotes.first().advance_required),
            "method": "cash", "kind": "advance", "idempotency_key": key})

    def deliver_all(self, order, item, parts=("1", "3")):
        self.action(self.store, order, "begin-preparation")
        for amount in parts:
            self.action(self.store, order, "deliveries", {"items": [{"item_id": item.pk, "quantity": amount}]})
            delivery = order.deliveries.latest("pk")
            self.action(self.store, order, f"deliveries/{delivery.pk}/status", {"status": "dispatched"})
            self.action(self.store, order, f"deliveries/{delivery.pk}/status", {"status": "delivered"})
            self.action(self.customer, order, f"deliveries/{delivery.pk}/confirm")

    def test_complete_order_partial_deliveries_receipt_cash_handover_settlement_and_rating(self):
        order, item = self.approved()
        quote = order.quotes.first()
        self.assertEqual(quote.total, Decimal("250000"))
        self.assertEqual(quote.advance_required, Decimal("125000"))
        self.assertEqual(quote.snapshot["estimated_delivery_minutes"], 50)
        self.assertEqual(quote.snapshot["store_net"], "48000.00")
        self.assertEqual(quote.snapshot["plumber_net"], "180000.00")
        self.paid_advance(order, receiver=self.plumber)
        payment = order.payments.get(kind="advance")
        receipt = Notification.objects.filter(user=self.customer, event="order.payment_received").latest("pk")
        self.assertEqual(receipt.payload["amount"], "125000.00")
        self.assertFalse(receipt.payload["fiscal"])
        self.deliver_all(order, item)
        self.assertEqual(order.deliveries.count(), 2)
        self.assertEqual(order.quotes.first().total, Decimal("250000"))
        self.action(self.plumber, order, "start-work")
        self.action(self.plumber, order, "complete-work")
        self.action(self.customer, order, "accept-work")
        self.action(self.staff, order, "payments", {"amount": "125000", "method": "terminal", "kind": "balance", "idempotency_key": "balance-1"})
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CLOSED)
        self.action(self.staff, order, "settlements", {"partner": "plumber", "amount": "180000", "idempotency_key": "settle-p"}, 400, staff=True)
        self.action(self.staff, order, f"payments/{payment.pk}/cash-handover", staff=True)
        self.assertTrue(CashHandover.objects.filter(payment=payment).exists())
        for partner, amount in (("plumber", "180000"), ("store", "48000")):
            payload = {"partner": partner, "amount": amount, "idempotency_key": f"settle-{partner}"}
            self.action(self.staff, order, "settlements", payload, staff=True)
            self.action(self.staff, order, "settlements", payload, staff=True)
        self.assertEqual(Settlement.objects.filter(order=order).count(), 2)
        self.action(self.customer, order, "rating", {"plumber_score": 5, "store_score": 4, "comment": "Yaxshi"})
        rating = Rating.objects.get(order=order)
        self.assertFalse(rating.approved)
        reviews_path = f"/api/v1/common/plumbers/{self.plumber_profile.pk}/reviews/"
        self.assertEqual(self.request(None, "get", reviews_path).data["count"], 0)
        self.action(self.staff, order, f"ratings/{rating.pk}/moderate", {"approved": True}, staff=True)
        public = self.request(None, "get", f"/api/v1/common/plumbers/{self.plumber_profile.pk}/")
        self.assertEqual(public.data["rating"], "5.00")
        self.assertNotIn("phone_number", public.data)
        reviews = self.request(None, "get", reviews_path)
        self.assertEqual(reviews.data["results"][0]["score"], 5)
        self.assertTrue(AuditEvent.objects.filter(actor=self.staff, action="order.settlement_recorded").exists())

    def test_validation_consent_phone_coordinates_and_unknown_fields(self):
        payload = {"region_id": self.region.pk, "service_group_id": self.group.pk, "address": "Test",
                   "latitude": "40.5", "longitude": "72.3", "consent": True}
        for changed in ({"consent": False}, {"latitude": "91"}, {"total": "1"}, {"service_group_id": 999999}):
            with self.subTest(changed=changed):
                self.request(self.customer, "post", "/api/v1/site/orders/", {**payload, **changed}, 404 if "service_group_id" in changed else 400)
        self.customer.phone_verified_at = None
        self.customer.save(update_fields=["phone_verified_at"])
        self.request(self.customer, "post", "/api/v1/site/orders/", payload, 400)
        self.assertEqual(Order.objects.count(), 0)

    def test_participant_privacy_and_action_permissions(self):
        order, _ = self.quoted()
        self.request(self.other, "get", f"/api/v1/site/orders/{order.pk}/", expected=404)
        self.action(self.other, order, "cancel", expected=404)
        self.request(self.customer, "get", "/api/v1/admin/orders/", expected=403)
        self.action(self.customer, order, "material-prices", expected=400)
        detail = self.request(self.customer, "get", f"/api/v1/site/orders/{order.pk}/").data
        self.assertEqual(detail["plumber"]["phone_number"], self.plumber.phone_number)
        self.assertNotIn("phone_number", detail["store"])
        self.assertNotIn("plumber_commission", detail["quotes"][0]["snapshot"])
        self.assertNotIn("store_net", detail["accounting"])
        public_store = self.request(None, "get", f"/api/v1/common/stores/{self.store_profile.pk}/").data
        self.assertNotIn("phone_number", public_store)
        self.assertNotIn("commission_rate", public_store)

    def test_every_order_action_rejects_anonymous_and_foreign_participants(self):
        order = self.create_order()
        actions = ("plumber-response", "inspection", "estimate", "store-response", "material-prices",
            "approve-quote", "reject-quote", "payments", "begin-preparation", "deliveries",
            "deliveries/1/status", "deliveries/1/confirm", "issues", "work-schedule", "start-work",
            "complete-work", "accept-work", "cancel", "rating", "attachments")
        for action in actions:
            with self.subTest(action=action):
                self.action(None, order, action, expected=401)
                self.action(self.other, order, action, expected=404)
        for action in ("eligible-plumbers", "available-stores"):
            self.request(self.customer, "get", f"/api/v1/admin/orders/{order.pk}/{action}/", expected=403)
        for action in ("assign-plumber", "assign-store", "confirm-urgent", "sign-contract", "resolve-dispute",
                       "refunds", "settlements", "payments/1/cash-handover", "ratings/1/moderate"):
            self.action(self.customer, order, action, expected=403, staff=True)

    def test_repricing_requires_current_version_new_contract_signature_and_advance_difference(self):
        order, item = self.approved()
        self.paid_advance(order)
        original = order.quotes.first()
        signed = Contract.objects.get(quote=original)
        old_text = signed.text_snapshot
        self.rate.unit_price = Decimal("999999")
        self.rate.save()
        self.price(order, item, price="20000")
        self.assertEqual(order.quotes.first().snapshot["service_total"], "200000.00")
        self.assertEqual(order.quotes.first().total, Decimal("290000"))
        self.action(self.customer, order, "approve-quote", {"quote_version": 1}, 400)
        self.action(self.customer, order, "approve-quote", {"quote_version": 2})
        self.action(self.store, order, "begin-preparation", expected=400)
        self.action(self.staff, order, "sign-contract", staff=True)
        self.action(self.store, order, "begin-preparation", expected=400)
        self.action(self.staff, order, "payments", {"amount": "20000", "kind": "advance", "method": "cash", "idempotency_key": "difference"})
        self.action(self.store, order, "begin-preparation")
        self.price_rejected(order, item)
        signed.refresh_from_db()
        self.assertEqual(signed.text_snapshot, old_text)
        self.assertIsNotNone(signed.signed_at)
        self.assertEqual(Quote.objects.filter(order=order).count(), 2)

    def price_rejected(self, order, item):
        self.action(self.store, order, "material-prices", {"items": [{"id": item.pk, "unit_price": "1", "available": True}],
            "delivery_fee": "0", "preparation_minutes": 0}, 400)

    def test_rejected_quote_blocks_same_plumber_and_requires_admin_reassignment(self):
        order, _ = self.quoted()
        self.action(self.customer, order, "reject-quote", {"quote_version": 1, "reason": "Qimmat"})
        self.action(self.customer, order, "cancel", expected=403)
        self.action(self.plumber, order, "estimate", {"services": [{"service_id": self.service.pk, "quantity": "1"}], "materials": []}, 400)
        self.action(self.staff, order, "assign-plumber", {"plumber_id": self.plumber.pk}, 404, staff=True)
        second = User.objects.create_user(username="second-plumber", role="plumber")
        profile = PlumberProfile.objects.create(user=second)
        profile.regions.add(self.region); profile.services.add(self.group)
        self.action(self.staff, order, "assign-plumber", {"plumber_id": second.pk}, staff=True)
        self.request(self.plumber, "get", f"/api/v1/site/orders/{order.pk}/", expected=404)

    def test_partner_decline_commits_and_returns_success_without_private_order(self):
        order = self.create_order()
        self.action(self.staff, order, "assign-plumber", {"plumber_id": self.plumber.pk}, staff=True)
        self.action(self.plumber, order, "plumber-response", {"accept": False, "reason": "Bandman"})
        order.refresh_from_db()
        self.assertIsNone(order.plumber_id)
        self.assertEqual(order.status, Order.Status.REQUESTED)
        self.assertTrue(Notification.objects.filter(user=self.staff, event="order.plumber_rejected").exists())

    def test_payment_idempotency_overpayment_and_collection_before_acceptance(self):
        order, _ = self.approved()
        self.paid_advance(order)
        self.paid_advance(order)
        self.assertEqual(Payment.objects.filter(order=order).count(), 1)
        self.action(self.staff, order, "payments", {"amount": "125001", "kind": "advance", "method": "cash", "idempotency_key": "advance-1"}, 400)
        self.action(self.staff, order, "payments", {"amount": "125001", "kind": "advance", "method": "cash", "idempotency_key": "overpaid"}, 400)
        self.action(self.staff, order, "payments", {"amount": "125000", "kind": "balance", "method": "cash", "idempotency_key": "too-early"}, 400)

    def test_cancellation_refunds_before_preparation_and_company_exception_after_start(self):
        order, _ = self.approved()
        self.paid_advance(order)
        self.action(self.customer, order, "cancel", {"reason": "Reja o‘zgardi"})
        payload = {"amount": "125000", "reason": "Ish boshlanmagan", "idempotency_key": "refund-1"}
        self.action(self.staff, order, "refunds", payload, staff=True)
        self.action(self.staff, order, "refunds", payload, staff=True)
        self.assertEqual(Refund.objects.filter(order=order).count(), 1)
        self.assertEqual(financial_summary(order)["net_paid"], Decimal("0"))
        order.refresh_from_db()
        self.assertEqual(financial_summary(order)["balance_due"], Decimal("0"))
        other_order, _ = self.approved()
        self.paid_advance(other_order, key="advance-2")
        self.action(self.store, other_order, "begin-preparation")
        self.action(self.customer, other_order, "cancel", {"reason": "Bekor"})
        self.action(self.staff, other_order, "refunds", {**payload, "idempotency_key": "refund-2"}, 400, staff=True)
        exception_order, _ = self.approved()
        self.paid_advance(exception_order, key="advance-3")
        self.action(self.store, exception_order, "begin-preparation")
        self.action(self.staff, exception_order, "cancel", {"reason": "Do‘kon bajarmadi", "company_failure": True}, staff=True)
        self.action(self.staff, exception_order, "refunds", {**payload, "idempotency_key": "refund-3"}, staff=True)

    def test_dispute_blocks_balance_and_settlements_until_staff_records_resolution(self):
        order, item = self.approved()
        self.paid_advance(order)
        self.deliver_all(order, item)
        self.action(self.plumber, order, "start-work")
        self.action(self.plumber, order, "complete-work")
        self.action(self.customer, order, "issues", {"description": "Suv sizmoqda"})
        self.action(self.customer, order, "accept-work", expected=400)
        self.action(self.staff, order, "payments", {"amount": "125000", "kind": "balance", "method": "cash", "idempotency_key": "disputed"}, 400)
        self.action(self.staff, order, "settlements", {"amount": "1", "partner": "plumber", "idempotency_key": "disputed-settle"}, 400, staff=True)
        self.action(self.staff, order, "resolve-dispute", {"note": "Kelishildi, kamchilik bartaraf qilindi", "accept_work": True}, staff=True)
        order.refresh_from_db()
        self.assertEqual(order.status, Order.Status.CUSTOMER_ACCEPTED)

    def test_repricing_refund_then_cancellation_can_return_all_remaining_money(self):
        order, item = self.approved()
        self.paid_advance(order)
        self.price(order, item, price="0", delivery_fee="0")
        self.action(self.staff, order, "refunds", {"amount": "25000", "reason": "Yangi avans kamroq", "idempotency_key": "reprice-refund"}, staff=True)
        self.action(self.customer, order, "cancel", {"reason": "Boshlashdan oldin"})
        self.action(self.staff, order, "refunds", {"amount": "100000", "reason": "Qolgan pul", "idempotency_key": "remaining-refund"}, staff=True)
        self.assertEqual(financial_summary(order)["net_paid"], Decimal("0"))

    def test_staff_can_authorize_company_failure_refund_after_customer_cancellation(self):
        order, _ = self.approved()
        self.paid_advance(order)
        self.action(self.store, order, "begin-preparation")
        self.action(self.customer, order, "cancel", {"reason": "Muammo"})
        self.action(self.staff, order, "cancel", {"reason": "Do‘kon aybi tasdiqlandi", "company_failure": True}, staff=True)
        self.action(self.staff, order, "refunds", {"amount": "125000", "reason": "Admin qarori", "idempotency_key": "late-authorized-refund"}, staff=True)
        self.assertEqual(financial_summary(order)["net_paid"], Decimal("0"))

    def test_paid_rejected_requote_can_be_refunded_and_reassigned_without_losing_cash_history(self):
        order, item = self.approved()
        self.paid_advance(order, receiver=self.plumber)
        payment = order.payments.get()
        self.price(order, item, price="20000")
        self.action(self.customer, order, "reject-quote", {"quote_version": order.quote_version})
        self.action(self.staff, order, "refunds", {"amount": "125000", "reason": "Smeta rad etildi", "idempotency_key": "rejected-refund"}, staff=True)
        second = User.objects.create_user(username="replacement-plumber", role="plumber")
        profile = PlumberProfile.objects.create(user=second)
        profile.regions.add(self.region)
        profile.services.add(self.group)
        self.action(self.staff, order, "assign-plumber", {"plumber_id": second.pk}, staff=True)
        self.action(self.staff, order, f"payments/{payment.pk}/cash-handover", staff=True)
        order.refresh_from_db()
        self.assertEqual(order.plumber_id, second.pk)
        self.assertEqual(financial_summary(order)["net_paid"], Decimal("0"))

    def test_delivery_overallocation_invalid_transition_and_premature_work(self):
        order, item = self.approved()
        self.paid_advance(order)
        self.action(self.plumber, order, "start-work", expected=400)
        self.action(self.store, order, "begin-preparation")
        self.action(self.store, order, "deliveries", {"items": [{"item_id": item.pk, "quantity": "5"}]}, 400)
        self.assertEqual(order.deliveries.count(), 0)
        self.action(self.store, order, "deliveries", {"items": [{"item_id": item.pk, "quantity": "4"}]})
        delivery = order.deliveries.get()
        self.action(self.store, order, f"deliveries/{delivery.pk}/status", {"status": "delivered"}, 400)
        self.action(self.customer, order, f"deliveries/{delivery.pk}/confirm", expected=400)

    @patch("apps.orders.services.timezone.localtime")
    def test_urgent_hours_admin_confirmation_and_one_flat_surcharge(self, local_clock):
        local_clock.return_value = timezone.now().replace(hour=12, minute=0, second=0)
        order = self.create_order(is_urgent=True)
        self.action(self.staff, order, "assign-plumber", {"plumber_id": self.plumber.pk}, 400, staff=True)
        self.action(self.staff, order, "confirm-urgent", {"confirmed": True}, staff=True)
        item = self.estimate(order)
        self.price(order, item)
        self.assertEqual(order.quotes.first().snapshot["urgent_fee"], "20000.00")
        self.center.working_days = [(timezone.localtime().weekday() + 1) % 7]
        self.center.save()
        payload = {"region_id": self.region.pk, "service_group_id": self.group.pk, "address": "Test",
                   "latitude": "40.5", "longitude": "72.3", "consent": True, "is_urgent": True}
        self.request(self.customer, "post", "/api/v1/site/orders/", payload, 400)

    def test_deadline_alert_once_without_automatic_reassignment(self):
        order = self.create_order()
        self.action(self.staff, order, "assign-plumber", {"plumber_id": self.plumber.pk}, staff=True)
        Order.objects.filter(pk=order.pk).update(response_due_at=timezone.now() - timedelta(minutes=1))
        call_command("scan_assignment_deadlines", stdout=BytesIOText())
        call_command("scan_assignment_deadlines", stdout=BytesIOText())
        self.assertEqual(Notification.objects.filter(user=self.staff, event="order.assignment_expired").count(), 1)
        order.refresh_from_db()
        self.assertEqual(order.plumber_id, self.plumber.pk)
        self.assertEqual(order.status, Order.Status.ASSIGNED)

    def test_protected_attachment_download_and_pdf_participant_scope(self):
        order = self.create_order()
        self.client.force_authenticate(self.customer)
        with tempfile.TemporaryDirectory() as directory, override_settings(MEDIA_ROOT=directory):
            file = SimpleUploadedFile("sample.png", b"\x89PNG\r\n\x1a\n" + b"fixture", content_type="image/png")
            response = self.client.post(f"/api/v1/site/orders/{order.pk}/attachments/", {"file": file, "purpose": "request"}, format="multipart")
            self.assertEqual(response.status_code, 201)
            path = response.data["download_path"]
            own = self.request(self.customer, "get", path)
            self.assertEqual(b"".join(own.streaming_content), b"\x89PNG\r\n\x1a\nfixture")
            own.close()
            self.request(self.other, "get", path, expected=404)
            self.request(None, "get", path, expected=401)
        quoted, _ = self.approved()
        contract = quoted.contracts.get()
        path = f"/api/v1/site/orders/{quoted.pk}/contracts/{contract.pk}/pdf/"
        with patch("apps.orders.documents.render_contract", return_value=b"%PDF-fixture"):
            self.assertEqual(self.request(self.customer, "get", path).content, b"%PDF-fixture")
            self.request(self.other, "get", path, expected=404)

    def test_reports_all_formats_and_filters_are_staff_only(self):
        order, _ = self.quoted()
        self.request(self.customer, "get", "/api/v1/admin/reports/", expected=403)
        report = self.request(self.staff, "get", "/api/v1/admin/reports/")
        self.assertEqual(report.data["count"], 1)
        csv = self.request(self.staff, "get", "/api/v1/admin/reports/?export=csv")
        self.assertIn(b"store_commission", csv.content)
        xlsx = self.request(self.staff, "get", "/api/v1/admin/reports/?export=xlsx")
        from openpyxl import load_workbook
        workbook = load_workbook(BytesIO(xlsx.content), read_only=True)
        rows = list(workbook["UZS"].values)
        self.assertEqual(rows[1][0], order.pk)
        workbook.close()
        self.request(self.staff, "get", "/api/v1/admin/reports/?date_from=2026-10-20&date_to=2026-10-01", expected=400)


class BytesIOText:
    def write(self, value):
        return len(value)

    def flush(self):
        pass
