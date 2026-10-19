"""Run on the separate verification machine, never on the write-only machine."""
from io import StringIO
from unittest.mock import patch

from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings

from apps.catalog.models import ServiceCenter
from apps.common.audit import AuditEvent
from apps.common.mock_seed import MANIFEST_ACTION, MockSeeder, PREVIEW_USERNAME, domain_models
from apps.orders.models import Attachment, Order
from apps.orders.selectors import financial_summary
from apps.tg_bot.models import BotUpdate, Notification
from apps.users.models import Consumer, PlumberProfile, User


class MockSeedTests(TestCase):
    def setUp(self):
        settings = override_settings(DEBUG=True, STORAGES={
            "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
            "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
        })
        settings.enable()
        self.addCleanup(settings.disable)

    def seed(self, **kwargs):
        output = StringIO()
        call_command("seed_mock", stdout=output, **kwargs)
        return output.getvalue()

    def counts(self):
        return {label: model.objects.count() for label, model in domain_models().items()}

    def test_default_covers_every_domain_model_with_valid_reconciled_records(self):
        with patch("requests.sessions.Session.request", side_effect=AssertionError("Seed must be offline")) as network:
            self.seed()
            network.assert_not_called()
        for label, model in domain_models().items():
            with self.subTest(model=label):
                self.assertGreaterEqual(model.objects.count(), 1 if model is ServiceCenter else 20)
                for instance in model.objects.all():
                    instance.full_clean()
        self.assertEqual(Order.objects.count(), 20)
        self.assertEqual(User.objects.count(), 61)
        self.assertEqual(Consumer.objects.count(), 21)  # Includes the synthetic staff user.
        self.assertEqual(AuditEvent.objects.filter(action=MANIFEST_ACTION).count(), 1)
        for order in Order.objects.all():
            summary = financial_summary(order)
            self.assertEqual(order.status, Order.Status.CLOSED)
            self.assertEqual(summary["net_paid"], summary["total"])
            self.assertEqual(summary["balance_due"], 0)
            self.assertEqual(summary["plumber_due"], 0)
            self.assertEqual(summary["store_due"], 0)
            self.assertGreater(summary["refunded"], 0)
            self.assertEqual(order.quotes.count(), 2)
            self.assertEqual(order.contracts.filter(signed_at__isnull=False).count(), 2)
            self.assertEqual(order.payments.count(), 2)
            self.assertFalse(order.issues.filter(resolved_at__isnull=True).exists())
            self.assertEqual(order.customer.username, PREVIEW_USERNAME)
            attachment = order.attachments.get()
            self.assertTrue(attachment.file.storage.exists(attachment.file.name))
            with attachment.file.open("rb") as content:
                self.assertEqual(content.read(8), b"\x89PNG\r\n\x1a\n")
        self.assertFalse(User.objects.filter(telegram_id__isnull=False).exists())
        self.assertTrue(all(not user.has_usable_password() for user in User.objects.all()))
        self.assertFalse(Notification.objects.filter(sent_at__isnull=True).exists())
        self.assertFalse(BotUpdate.objects.filter(update_id__gte=0).exists())

    def test_rerun_is_a_noop_and_changed_options_do_not_overwrite(self):
        self.seed(count=2, prefix="repeat", no_local_preview=True)
        counts = self.counts()
        manifest = AuditEvent.objects.get(action=MANIFEST_ACTION)
        output = self.seed(count=2, prefix="repeat", no_local_preview=True)
        self.assertIn("yangi nusxa qo‘shilmadi", output)
        self.assertEqual(counts, self.counts())
        manifest.refresh_from_db()
        self.assertEqual(len(manifest.payload["records"]["orders.Order"]), 2)
        for options in ({"count": 3, "no_local_preview": True}, {"count": 2, "no_local_preview": False}):
            with self.assertRaises(CommandError):
                self.seed(prefix="repeat", **options)
        self.assertEqual(counts, self.counts())

    def test_invalid_options_and_production_are_rejected_without_writes(self):
        before = self.counts()
        for options in ({"count": 0}, {"count": 201}, {"prefix": "../unsafe"}, {"prefix": "UPPER"}):
            with self.assertRaises(CommandError):
                self.seed(**options)
        with override_settings(DEBUG=True, SETTINGS_MODULE="project_backend.settings.production"):
            with self.assertRaisesMessage(CommandError, "faqat development/test"):
                self.seed()
        with override_settings(DEBUG=False, SETTINGS_MODULE="custom.settings"):
            with self.assertRaises(CommandError):
                self.seed()
        self.assertEqual(before, self.counts())

    def test_failed_batch_rolls_back_database_and_only_removes_its_own_files(self):
        storage = Attachment._meta.get_field("file").storage
        existing = storage.save("mock/failed/plumber-001.png", ContentFile(b"keep me"))
        original_create = MockSeeder.create

        def fail_at_end(seeder, model, **values):
            if model is BotUpdate:
                raise RuntimeError("forced seed failure")
            return original_create(seeder, model, **values)

        before = self.counts()
        with patch.object(MockSeeder, "create", new=fail_at_end):
            with self.assertRaisesMessage(CommandError, "forced seed failure"):
                self.seed(count=1, prefix="failed", no_local_preview=True)
        self.assertEqual(before, self.counts())
        self.assertFalse(storage.exists("mock/failed/completion-001.png"))
        self.assertTrue(storage.exists(existing))
        self.assertEqual(storage.listdir("mock/failed")[1], ["plumber-001.png"])
        with storage.open(existing, "rb") as content:
            self.assertEqual(content.read(), b"keep me")

    def test_existing_center_and_preview_identity_are_preserved(self):
        self.seed(count=1, prefix="first")
        center = ServiceCenter.objects.get()
        center.name = "Mavjud markaz"
        center.save()
        preview = User.objects.get(username=PREVIEW_USERNAME)
        preview.first_name = "Existing preview name"
        preview.save()
        self.seed(count=1, prefix="second")
        center.refresh_from_db()
        preview.refresh_from_db()
        self.assertEqual(center.name, "Mavjud markaz")
        self.assertEqual(preview.first_name, "Existing preview name")
        self.assertEqual(ServiceCenter.objects.count(), 1)
        self.assertEqual(Order.objects.filter(customer=preview).count(), 2)

    def test_reserved_name_collision_never_changes_existing_account(self):
        user = User.objects.create_user(username=PREVIEW_USERNAME, password="existing-password", is_staff=True)
        before = self.counts()
        with self.assertRaisesMessage(CommandError, "Reserved preview akkaunti"):
            self.seed(count=1)
        user.refresh_from_db()
        self.assertTrue(user.is_staff)
        self.assertTrue(user.check_password("existing-password"))
        self.assertEqual(before, self.counts())

    def test_missing_seed_files_are_reported_instead_of_creating_duplicates(self):
        self.seed(count=1, prefix="missing", no_local_preview=True)
        profile = PlumberProfile.objects.get()
        profile.photo.storage.delete(profile.photo.name)
        counts = self.counts()
        with self.assertRaisesMessage(CommandError, "mock fayli o‘chirilgan"):
            self.seed(count=1, prefix="missing", no_local_preview=True)
        self.assertEqual(counts, self.counts())
