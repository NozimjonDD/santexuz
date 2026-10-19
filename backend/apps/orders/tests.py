"""PostgreSQL concurrency tests; only run on the other machine."""
from concurrent.futures import ThreadPoolExecutor
from decimal import Decimal
from threading import Barrier
from unittest import skipUnless

from django.db import connection, connections
from django.test import TransactionTestCase
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from apps.catalog.models import Region, ServiceGroup
from apps.orders import services
from apps.orders.models import Contract, Order, Payment, Quote
from apps.users.models import User


@skipUnless(connection.vendor == "postgresql", "PostgreSQL row locks are required")
class PaymentConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.staff = User.objects.create_user(username="concurrent-staff", is_staff=True)
        self.customer = User.objects.create_user(username="concurrent-customer")
        region = Region.objects.create(code="concurrent-region", name="Test")
        group = ServiceGroup.objects.create(code="concurrent-group", name="Test")
        self.order = Order.objects.create(customer=self.customer, region=region, service_group=group,
            address="Test", latitude=40, longitude=72, consent_at=timezone.now(), phone_snapshot="+998901234567",
            status=Order.Status.APPROVED, quote_version=1, approved_version=1)
        quote = Quote.objects.create(order=self.order, version=1, snapshot={}, total="100", advance_required="50")
        Contract.objects.create(order=self.order, quote=quote, language="uz", template_version=1,
            text_snapshot="Concurrency fixture", parties_snapshot={}, signed_at=timezone.now(), signed_by=self.staff)

    def concurrent_payments(self, keys):
        barrier = Barrier(2)
        actor_id, order_id = self.staff.pk, self.order.pk

        def collect(key):
            try:
                actor = User.objects.get(pk=actor_id)
                barrier.wait(timeout=15)
                try:
                    item = services.record_payment(actor, order_id, Decimal("50"), "cash", "advance", key)
                    return ("recorded", item.pk)
                except ValidationError:
                    return ("rejected", None)
            finally:
                connections.close_all()

        with ThreadPoolExecutor(max_workers=2) as pool:
            futures = [pool.submit(collect, key) for key in keys]
            return [future.result(timeout=30) for future in futures]

    def test_same_key_is_one_payment_under_concurrent_requests(self):
        results = self.concurrent_payments(("same-key", "same-key"))
        self.assertEqual(results[0], results[1])
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)

    def test_different_keys_cannot_both_exceed_advance(self):
        results = self.concurrent_payments(("first-key", "second-key"))
        self.assertEqual(sorted(result[0] for result in results), ["recorded", "rejected"])
        self.assertEqual(Payment.objects.filter(order=self.order).count(), 1)
