from datetime import timedelta
from io import StringIO
from types import SimpleNamespace
from unittest.mock import patch

from django.core.management import call_command
from django.core.management.base import CommandError
from django.db import transaction
from django.test import TestCase, override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from apps.tg_bot.models import Notification
from apps.tg_bot.services import enqueue, notification_text
from apps.users.models import User


@override_settings(MINI_APP_URL="https://miniapp.example.test/", TELEGRAM_WEBHOOK_SECRET="test-webhook-secret-with-at-least-32-characters")
class WebhookSetupTests(TestCase):
    def test_inspection_does_not_register_or_send_messages(self):
        with patch("apps.tg_bot.management.commands.configure_telegram_webhook.bot_call", return_value={
            "url": "https://miniapp.example.test/telegram/webhook/", "pending_update_count": 0,
        }) as request:
            call_command("configure_telegram_webhook", stdout=StringIO())
        request.assert_called_once_with("getWebhookInfo", {})

    def test_explicit_registration_preserves_pending_updates(self):
        with patch("apps.tg_bot.management.commands.configure_telegram_webhook.bot_call", side_effect=[True, True, {
            "url": "https://miniapp.example.test/telegram/webhook/", "pending_update_count": 2,
        }]) as request:
            call_command("configure_telegram_webhook", register=True, stdout=StringIO())
        webhook = request.call_args_list[0].args
        self.assertEqual(webhook[0], "setWebhook")
        self.assertFalse(webhook[1]["drop_pending_updates"])
        self.assertEqual(webhook[1]["allowed_updates"], ["message"])
        self.assertEqual(webhook[1]["secret_token"], "test-webhook-secret-with-at-least-32-characters")
        self.assertEqual(request.call_args_list[1].args[0], "setChatMenuButton")

    def test_missing_or_failed_webhook_fails_without_raw_provider_details(self):
        with patch("apps.tg_bot.management.commands.configure_telegram_webhook.bot_call", return_value={"url": ""}):
            with self.assertRaises(CommandError):
                call_command("configure_telegram_webhook", stdout=StringIO())
        with patch("apps.tg_bot.management.commands.configure_telegram_webhook.bot_call", side_effect=RuntimeError("telegram_delivery_failed")):
            with self.assertRaisesMessage(CommandError, "telegram_delivery_failed"):
                call_command("configure_telegram_webhook", stdout=StringIO())


class NotificationTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="recipient", telegram_id=501, language="uz")

    def test_outbox_rolls_back_with_business_transaction(self):
        with self.assertRaises(ValueError):
            with transaction.atomic():
                enqueue(self.user, "order.created", 12)
                raise ValueError("business operation failed")
        self.assertFalse(Notification.objects.exists())

    @override_settings(MINI_APP_URL="https://example.test/")
    def test_worker_sends_contact_and_miniapp_buttons_and_marks_sent(self):
        item = enqueue(self.user, "bot.welcome")
        with patch("apps.tg_bot.management.commands.deliver_notifications.bot_call", return_value={}) as send:
            call_command("deliver_notifications", limit=10, stdout=StringIO())
            call_command("deliver_notifications", limit=10, stdout=StringIO())
        self.assertEqual(send.call_count, 1)
        keyboard = send.call_args.args[1]["reply_markup"]["keyboard"]
        self.assertTrue(keyboard[0][0]["request_contact"])
        self.assertEqual(keyboard[1][0]["web_app"]["url"], "https://example.test/")
        item.refresh_from_db()
        self.assertIsNotNone(item.sent_at)

    def test_failed_delivery_retains_outbox_and_retries_after_backoff(self):
        item = enqueue(self.user, "order.created", 12)
        with patch("apps.tg_bot.management.commands.deliver_notifications.bot_call", side_effect=RuntimeError("telegram_delivery_failed")):
            call_command("deliver_notifications", stdout=StringIO())
        item.refresh_from_db()
        self.assertIsNone(item.sent_at)
        self.assertEqual(item.attempts, 1)
        self.assertGreater(item.next_attempt_at, timezone.now())
        with patch("apps.tg_bot.management.commands.deliver_notifications.bot_call", return_value={}) as send:
            call_command("deliver_notifications", stdout=StringIO())
            self.assertFalse(send.called)
            Notification.objects.filter(pk=item.pk).update(next_attempt_at=timezone.now() - timedelta(seconds=1))
            call_command("deliver_notifications", stdout=StringIO())
        item.refresh_from_db()
        self.assertIsNotNone(item.sent_at)
        self.assertEqual(item.attempts, 2)

    def test_receipts_and_eta_are_localized_without_fiscal_claim(self):
        for language in ("uz", "ru", "en"):
            self.user.language = language
            item = Notification(user=self.user, event="order.payment_received", order_id=12,
                payload={"amount": "50000", "method": "cash", "received_at": "2026-10-18", "receiver": "Operator"})
            text = notification_text(item)
            for expected in ("50000 UZS", "cash", "2026-10-18", "Operator"):
                self.assertIn(expected, text)
        item = Notification(user=self.user, event="order.delivery_updated", order_id=12, payload={"eta": "2026-10-18T12:00:00Z"})
        self.assertIn("2026-10-18T12:00:00Z", notification_text(item))


class NotificationAPITests(APITestCase):
    def test_inbox_and_read_are_scoped_to_owner(self):
        owner = User.objects.create_user(username="owner")
        other = User.objects.create_user(username="other")
        item = enqueue(owner, "order.created", 12)
        enqueue(other, "order.created", 99)
        self.client.force_authenticate(owner)
        response = self.client.get("/api/v1/auth/notifications/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data["count"], 1)
        self.assertEqual(self.client.post(f"/api/v1/auth/notifications/{item.pk}/read/").status_code, 200)
        item.refresh_from_db()
        self.assertIsNotNone(item.read_at)
        self.client.force_authenticate(other)
        self.assertEqual(self.client.post(f"/api/v1/auth/notifications/{item.pk}/read/").status_code, 404)
