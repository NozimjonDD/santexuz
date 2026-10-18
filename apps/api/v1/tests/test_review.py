"""Regression cases authored here; execute only on the verification machine."""
from django.contrib.auth import authenticate
from django.db import DatabaseError, connection, transaction
from django.test import TestCase, override_settings
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken

from apps.api.v1.admin.views import ReportView
from apps.catalog.models import Region, ServiceGroup
from apps.orders.models import CashHandover, Contract, Order, OrderEvent, Payment, Quote, Refund, Settlement
from apps.orders.selectors import financial_queryset, financial_summary
from apps.users.models import User


class DeletedAccountTests(TestCase):
    def test_deleted_account_cannot_use_password_access_or_refresh(self):
        user = User.objects.create_user(username="deleted", password="Fixture-only-901!", is_staff=True)
        token = RefreshToken.for_user(user)
        user.is_deleted = True
        user.save(update_fields=["is_deleted"])
        self.assertIsNone(authenticate(username="deleted", password="Fixture-only-901!"))
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + str(token.access_token))
        self.assertEqual(client.get("/api/v1/auth/me/").status_code, 401)
        client.credentials()
        self.assertEqual(client.post("/api/v1/auth/refresh/", {"refresh": str(token)}, format="json").status_code, 401)

    def test_deleted_catalog_relations_cannot_be_reintroduced_through_staff_writes(self):
        user = User.objects.create_user(username="staff-review", is_staff=True)
        group = ServiceGroup.objects.create(name="Archived", code="archived", is_deleted=True)
        client = APIClient()
        client.force_authenticate(user)
        response = client.post("/api/v1/admin/services/", {"name": "New", "unit": "dona", "group": group.pk}, format="json")
        self.assertEqual(response.status_code, 400)

    @override_settings(DEBUG=False, DEV_LOCAL_LOGIN=False)
    def test_production_template_does_not_offer_role_or_design_preview_controls(self):
        response = self.client.get("/")
        self.assertNotContains(response, 'id="design-preview"')
        self.assertNotContains(response, 'id="demo-role"')
        self.assertContains(response, 'data-local-preview="false"')


class FinancialReadTests(TestCase):
    def setUp(self):
        self.customer = User.objects.create_user(username="financial-customer")
        self.receiver = User.objects.create_user(username="financial-staff", is_staff=True)
        self.region = Region.objects.create(name="Marhamat", code="finance")
        self.group = ServiceGroup.objects.create(name="Repair", code="finance-repair")

    def order(self):
        return Order.objects.create(customer=self.customer, region=self.region, service_group=self.group,
            address="Fixture", latitude="40", longitude="72", phone_snapshot="+998901234567", consent_at=timezone.now())

    def test_order_buckets_filter_before_pagination_and_preserve_customer_scope(self):
        active = self.order()
        finished = self.order()
        Order.objects.filter(pk=finished.pk).update(status=Order.Status.CLOSED)
        foreign = self.order()
        other = User.objects.create_user(username="foreign-financial-customer")
        Order.objects.filter(pk=foreign.pk).update(customer=other)
        client = APIClient()
        client.force_authenticate(self.customer)
        active_page = client.get("/api/v1/site/orders/?bucket=active")
        history_page = client.get("/api/v1/site/orders/?bucket=history")
        self.assertEqual([row["id"] for row in active_page.data["results"]], [active.pk])
        self.assertEqual([row["id"] for row in history_page.data["results"]], [finished.pk])
        self.assertEqual(client.get("/api/v1/site/orders/?bucket=invalid").status_code, 400)

    def test_all_journal_tables_and_signed_contracts_reject_raw_mutation(self):
        order = self.order()
        quote = Quote.objects.create(order=order, version=1, snapshot={}, total="100", advance_required="50")
        payment = Payment.objects.create(order=order, amount="10", method="cash", kind="advance",
            received_by=self.receiver, idempotency_key="guard-payment")
        instances = [quote, payment,
            Refund.objects.create(order=order, amount="1", reason="Fixture", recorded_by=self.receiver, idempotency_key="guard-refund"),
            Settlement.objects.create(order=order, partner="plumber", amount="1", recorded_by=self.receiver, idempotency_key="guard-settlement"),
            CashHandover.objects.create(payment=payment, confirmed_by=self.receiver),
            OrderEvent.objects.create(order=order, actor=self.receiver, action="fixture", status=order.status),
            Contract.objects.create(order=order, quote=quote, language="uz", template_version=1,
                text_snapshot="Fixture", signed_at=timezone.now(), signed_by=self.receiver),
        ]
        for instance in instances:
            table = connection.ops.quote_name(instance._meta.db_table)
            for statement in (f"UPDATE {table} SET is_deleted = TRUE WHERE id = %s", f"DELETE FROM {table} WHERE id = %s"):
                with self.subTest(table=table, statement=statement):
                    with self.assertRaises(DatabaseError), transaction.atomic():
                        with connection.cursor() as cursor:
                            cursor.execute(statement, [instance.pk])

    def test_journal_sums_do_not_multiply_across_multiple_payments_and_refunds(self):
        order = self.order()
        Quote.objects.create(order=order, version=1, snapshot={"plumber_net": "60", "store_net": "30"}, total="100", advance_required="50")
        Order.objects.filter(pk=order.pk).update(quote_version=1)
        for number, amount in enumerate(("30", "40")):
            Payment.objects.create(order=order, amount=amount, method="cash", kind="advance", received_by=self.receiver, idempotency_key=f"review-payment-{number}")
        for number, amount in enumerate(("5", "10")):
            Refund.objects.create(order=order, amount=amount, reason="Fixture", recorded_by=self.receiver, idempotency_key=f"review-refund-{number}")
        baseline = financial_summary(Order.objects.get(pk=order.pk))
        annotated = financial_summary(financial_queryset(Order.objects.all()).get(pk=order.pk))
        self.assertEqual(annotated, baseline)
        self.assertEqual(annotated["paid"], 70)
        self.assertEqual(annotated["refunded"], 15)
        self.assertEqual(annotated["balance_due"], 45)

    def test_report_query_count_does_not_grow_for_each_order_in_one_chunk(self):
        def quoted_order():
            order = self.order()
            Quote.objects.create(order=order, version=1, snapshot={}, total="100", advance_required="50")
            Order.objects.filter(pk=order.pk).update(quote_version=1)

        quoted_order()
        with CaptureQueriesContext(connection) as small:
            list(ReportView.rows(financial_queryset(Order.objects.all())))
        for _ in range(8):
            quoted_order()
        with CaptureQueriesContext(connection) as larger:
            rows = list(ReportView.rows(financial_queryset(Order.objects.all())))
        self.assertEqual(len(rows), 9)
        self.assertEqual(len(larger), len(small))
