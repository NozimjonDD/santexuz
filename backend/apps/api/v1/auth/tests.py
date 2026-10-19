"""Authentication regressions; execute only on the runtime/test machine."""
import hashlib
import hmac
import json
from unittest.mock import patch
from urllib.parse import urlencode

from django.conf import settings
from django.core.cache import cache
from django.test import override_settings
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import AccessToken, RefreshToken

from apps.common.audit import AuditEvent
from apps.tg_bot.models import BotUpdate, Notification
from apps.users.models import User


NOW = 1_900_000_000
BOT_TOKEN = "123456789:isolated-auth-test-token"
WEBHOOK_SECRET = "isolated-webhook-secret-not-for-production"


def signed_init_data(telegram_id=501, auth_date=NOW, **user_fields):
    user = {"id": telegram_id, "first_name": "Ali", **user_fields}
    fields = {"auth_date": str(auth_date), "query_id": "test-query", "user": json.dumps(user, separators=(",", ":"))}
    data_check = "\n".join(f"{key}={value}" for key, value in sorted(fields.items()))
    secret = hmac.new(b"WebAppData", BOT_TOKEN.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


@override_settings(TELEGRAM_BOT_TOKEN=BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET=WEBHOOK_SECRET, TELEGRAM_INIT_DATA_MAX_AGE=300)
class AuthenticationTests(APITestCase):
    def setUp(self):
        cache.clear()
        throttle = patch("rest_framework.throttling.ScopedRateThrottle.allow_request", return_value=True)
        throttle.start()
        self.addCleanup(throttle.stop)
        clock = patch("apps.api.v1.auth.services.time.time", return_value=NOW)
        clock.start()
        self.addCleanup(clock.stop)

    def login(self, raw=None, **extra):
        return self.client.post(reverse("telegram-login"), {"init_data": raw or signed_init_data(), **extra}, format="json")

    def test_valid_signature_creates_customer_with_unusable_password(self):
        response = self.login(language="ru")
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(telegram_id=501)
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertEqual(user.language, "ru")
        self.assertFalse(user.has_usable_password())
        self.assertFalse(user.is_staff)
        self.assertEqual(str(AccessToken(response.data["access"])["user_id"]), str(user.pk))
        self.assertTrue(AuditEvent.objects.filter(actor=user, action="auth.telegram_login").exists())

    def test_signature_tampering_is_rejected_without_creating_account(self):
        raw = signed_init_data().replace("Ali", "Mallory")
        self.assertEqual(self.login(raw).status_code, 401)
        self.assertFalse(User.objects.filter(telegram_id=501).exists())

    def test_stale_and_future_signatures_are_rejected(self):
        for timestamp in (NOW - 301, NOW + 31):
            with self.subTest(timestamp=timestamp):
                self.assertEqual(self.login(signed_init_data(auth_date=timestamp)).status_code, 401)
        self.assertFalse(User.objects.exists())

    def test_duplicate_fields_are_rejected_even_with_valid_original_signature(self):
        response = self.login(signed_init_data() + "&auth_date=" + str(NOW))
        self.assertEqual(response.status_code, 401)

    def test_non_integer_and_bot_telegram_identities_are_rejected(self):
        for raw in (signed_init_data(telegram_id=True), signed_init_data(telegram_id="501"), signed_init_data(is_bot=True)):
            with self.subTest(raw=raw):
                self.assertEqual(self.login(raw).status_code, 401)
        self.assertFalse(User.objects.exists())

    def test_existing_inactive_user_cannot_login(self):
        user = User.objects.create_user(username="inactive", telegram_id=501, is_active=False)
        self.assertEqual(self.login().status_code, 401)
        self.assertFalse(AuditEvent.objects.filter(actor=user, action="auth.telegram_login").exists())

    def test_telegram_payload_cannot_grant_roles_or_staff_access(self):
        response = self.login(signed_init_data(role="store", is_staff=True, phone_number="+998901234567"))
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(telegram_id=501)
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.phone_number, "")
        self.assertIsNone(user.phone_verified_at)

    def test_existing_partner_role_is_preserved_during_telegram_login(self):
        user = User.objects.create_user(username="plumber", telegram_id=501, role=User.Role.PLUMBER)
        self.assertEqual(self.login(signed_init_data(role="customer")).status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.role, User.Role.PLUMBER)

    def test_profile_requires_authentication_and_prevents_privilege_and_phone_changes(self):
        self.assertEqual(self.client.get(reverse("profile")).status_code, 401)
        user = User.objects.create_user(username="profile-user", phone_number="+998901234567")
        self.client.force_authenticate(user)
        response = self.client.patch(reverse("profile"), {"first_name": "New name", "language": "en", "role": "store", "is_staff": True, "phone_number": "+998991111111", "phone_verified_at": "2026-10-18T00:00:00Z"}, format="json")
        self.assertEqual(response.status_code, 200)
        user.refresh_from_db()
        self.assertEqual(user.first_name, "New name")
        self.assertEqual(user.language, "en")
        self.assertEqual(user.role, User.Role.CUSTOMER)
        self.assertFalse(user.is_staff)
        self.assertEqual(user.phone_number, "+998901234567")
        self.assertIsNone(user.phone_verified_at)

    def test_staff_login_rejects_customer_and_accepts_separate_staff_account(self):
        User.objects.create_user(username="customer-login", password="RuntimeTestPassword!", role=User.Role.CUSTOMER)
        User.objects.create_user(username="staff-login", password="RuntimeTestPassword!", is_staff=True)
        customer_response = self.client.post(reverse("staff-login"), {"username": "customer-login", "password": "RuntimeTestPassword!"}, format="json")
        self.assertEqual(customer_response.status_code, 400)
        self.assertNotIn("access", customer_response.data)
        response = self.client.post(reverse("staff-login"), {"username": "staff-login", "password": "RuntimeTestPassword!"}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertIn("access", response.data)

    def test_inactive_staff_cannot_login(self):
        User.objects.create_user(username="disabled-staff", password="RuntimeTestPassword!", is_staff=True, is_active=False)
        response = self.client.post(reverse("staff-login"), {"username": "disabled-staff", "password": "RuntimeTestPassword!"}, format="json")
        self.assertEqual(response.status_code, 401)

    def test_refresh_keeps_token_owner_and_rotates_previous_refresh(self):
        owner = User.objects.create_user(username="token-owner")
        original = str(RefreshToken.for_user(owner))
        response = self.client.post(reverse("token-refresh"), {"refresh": original}, format="json")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(AccessToken(response.data["access"])["user_id"]), str(owner.pk))
        self.assertIn("refresh", response.data)
        self.assertNotEqual(original, response.data["refresh"])
        self.assertEqual(self.client.post(reverse("token-refresh"), {"refresh": original}, format="json").status_code, 401)

    def test_refresh_rejects_inactive_owner_and_forged_token(self):
        owner = User.objects.create_user(username="deactivated-owner")
        refresh = str(RefreshToken.for_user(owner))
        owner.is_active = False
        owner.save(update_fields=["is_active"])
        self.assertEqual(self.client.post(reverse("token-refresh"), {"refresh": refresh}, format="json").status_code, 401)
        self.assertEqual(self.client.post(reverse("token-refresh"), {"refresh": refresh + "tampered"}, format="json").status_code, 401)

    def test_logout_cannot_blacklist_another_users_refresh(self):
        owner = User.objects.create_user(username="refresh-owner")
        other = User.objects.create_user(username="other-user")
        refresh = str(RefreshToken.for_user(owner))
        self.client.force_authenticate(other)
        response = self.client.post(reverse("logout"), {"refresh": refresh}, format="json")
        self.assertEqual(response.status_code, 400)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post(reverse("token-refresh"), {"refresh": refresh}, format="json").status_code, 200)

    def test_logout_blacklists_own_refresh_and_requires_authentication(self):
        owner = User.objects.create_user(username="logout-owner")
        refresh = str(RefreshToken.for_user(owner))
        self.assertEqual(self.client.post(reverse("logout"), {"refresh": refresh}, format="json").status_code, 401)
        self.client.force_authenticate(owner)
        self.assertEqual(self.client.post(reverse("logout"), {"refresh": refresh}, format="json").status_code, 204)
        self.client.force_authenticate(None)
        self.assertEqual(self.client.post(reverse("token-refresh"), {"refresh": refresh}, format="json").status_code, 401)


@override_settings(TELEGRAM_BOT_TOKEN=BOT_TOKEN, TELEGRAM_WEBHOOK_SECRET=WEBHOOK_SECRET)
class TelegramContactWebhookTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="contact-owner", telegram_id=801)

    def update(self, update_id=1, contact_user_id=801, chat_type="private", phone="998 90 123 45 67"):
        return {"update_id": update_id, "message": {"from": {"id": 801}, "chat": {"id": 801, "type": chat_type}, "contact": {"user_id": contact_user_id, "phone_number": phone}}}

    def post(self, payload, secret=WEBHOOK_SECRET):
        return self.client.post(reverse("telegram-webhook"), payload, format="json", HTTP_X_TELEGRAM_BOT_API_SECRET_TOKEN=secret)

    def test_own_private_contact_is_verified_and_duplicate_update_is_idempotent(self):
        self.assertEqual(self.post(self.update()).status_code, 200)
        self.user.refresh_from_db()
        verified_at = self.user.phone_verified_at
        self.assertEqual(self.user.phone_number, "+998901234567")
        self.assertIsNotNone(verified_at)
        self.assertEqual(Notification.objects.filter(user=self.user, event="phone.verified").count(), 1)
        self.assertEqual(self.post(self.update(phone="998991111111")).status_code, 200)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "+998901234567")
        self.assertEqual(self.user.phone_verified_at, verified_at)
        self.assertEqual(BotUpdate.objects.filter(update_id=1).count(), 1)
        self.assertEqual(AuditEvent.objects.filter(actor=self.user, action="auth.phone_verified").count(), 1)

    def test_foreign_contact_is_rejected_without_verifying_phone(self):
        for update_id in (2, 2):
            self.assertEqual(self.post(self.update(update_id=update_id, contact_user_id=999)).status_code, 400)
        self.user.refresh_from_db()
        self.assertEqual(self.user.phone_number, "")
        self.assertIsNone(self.user.phone_verified_at)
        self.assertFalse(Notification.objects.filter(user=self.user).exists())

    def test_group_contact_and_foreign_chat_cannot_verify_phone(self):
        self.assertEqual(self.post(self.update(chat_type="group")).status_code, 200)
        payload = self.update(update_id=3)
        payload["message"]["chat"]["id"] = 999
        self.assertEqual(self.post(payload).status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.phone_verified_at)

    def test_webhook_rejects_wrong_secret_and_invalid_phone(self):
        self.assertEqual(self.post(self.update(), secret="invalid").status_code, 403)
        self.assertFalse(BotUpdate.objects.exists())
        self.assertEqual(self.post(self.update(phone="not-a-phone")).status_code, 400)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.phone_verified_at)

    def test_inactive_user_contact_is_ignored(self):
        self.user.is_active = False
        self.user.save(update_fields=["is_active"])
        self.assertEqual(self.post(self.update()).status_code, 200)
        self.user.refresh_from_db()
        self.assertIsNone(self.user.phone_verified_at)

    def test_first_start_bootstraps_customer_and_welcome_outbox(self):
        payload = {"update_id": 100, "message": {"from": {"id": 9001, "first_name": "New"}, "chat": {"id": 9001, "type": "private"}, "text": "/start"}}
        self.assertEqual(self.post(payload).status_code, 200)
        new_user = User.objects.get(telegram_id=9001)
        self.assertEqual(new_user.role, User.Role.CUSTOMER)
        self.assertFalse(new_user.is_staff)
        self.assertFalse(new_user.has_usable_password())
        self.assertTrue(Notification.objects.filter(user=new_user, event="bot.welcome").exists())
