"""Local preview boundary tests; run only on the other machine."""
from django.test import RequestFactory, TestCase, override_settings
from django.middleware.csrf import get_token
from django.conf import settings
from rest_framework.test import APIClient

from apps.api.v1.auth.development import LocalPreviewLoginView
from apps.common.development import local_preview_enabled
from apps.users.models import User


@override_settings(DEBUG=True, DEV_LOCAL_LOGIN=True, ALLOWED_HOSTS=["localhost", "127.0.0.1", "testserver", "example.test", "[::1]"])
class LocalPreviewTests(TestCase):
    def setUp(self):
        self.factory = RequestFactory()

    def login(self, host="localhost", remote="127.0.0.1"):
        request = self.factory.post("/api/v1/auth/dev-local/", data='{"language":"uz"}', content_type="application/json", HTTP_HOST=host, REMOTE_ADDR=remote)
        # This helper exercises the view boundary; the separate client test exercises CSRF.
        request._dont_enforce_csrf_checks = True
        return LocalPreviewLoginView.as_view()(request)

    def test_local_preview_creates_only_reserved_customer_and_reuses_it(self):
        response = self.login()
        self.assertEqual(response.status_code, 200)
        user = User.objects.get(username="__santex_local_preview__")
        self.assertEqual(user.role, "customer")
        self.assertFalse(user.is_staff)
        self.assertIsNone(user.telegram_id)
        self.assertFalse(user.has_usable_password())
        self.assertIsNotNone(user.phone_verified_at)
        self.assertEqual(self.login().data["user"]["id"], user.pk)

    def test_debug_flag_loopback_and_host_are_required(self):
        with override_settings(DEBUG=False):
            self.assertEqual(self.login().status_code, 404)
        with override_settings(DEV_LOCAL_LOGIN=False):
            self.assertEqual(self.login().status_code, 404)
        self.assertEqual(self.login(remote="192.168.1.2").status_code, 404)
        self.assertEqual(self.login(host="example.test").status_code, 404)
        self.assertFalse(User.objects.exists())

    def test_existing_real_account_collision_does_not_grant_access(self):
        User.objects.create_user(username="__santex_local_preview__", is_staff=True)
        self.assertEqual(self.login().status_code, 404)

    def test_page_only_exposes_preview_in_local_development(self):
        client = APIClient(enforce_csrf_checks=True)
        page = client.get("/", HTTP_HOST="localhost")
        self.assertContains(page, 'id="dev-login"')
        blocked = client.post("/api/v1/auth/dev-local/", {}, format="json", HTTP_HOST="localhost")
        # URL is deliberately absent under test/production URL configurations.
        self.assertIn(blocked.status_code, (403, 404))
        with override_settings(DEBUG=False):
            self.assertNotContains(client.get("/", HTTP_HOST="localhost"), 'id="dev-login"')

    def test_csrf_is_required_by_view_and_ipv6_loopback_is_supported(self):
        request = self.factory.post("/api/v1/auth/dev-local/", HTTP_HOST="localhost", REMOTE_ADDR="127.0.0.1")
        self.assertEqual(LocalPreviewLoginView.as_view()(request).status_code, 403)
        request = self.factory.get("/", HTTP_HOST="[::1]:8000", REMOTE_ADDR="::1")
        self.assertTrue(local_preview_enabled(request))

    def test_valid_csrf_allows_local_login(self):
        request = self.factory.post("/api/v1/auth/dev-local/", data='{"language":"uz"}', content_type="application/json", HTTP_HOST="localhost", REMOTE_ADDR="127.0.0.1")
        request.META["HTTP_X_CSRFTOKEN"] = get_token(request)
        request.COOKIES[settings.CSRF_COOKIE_NAME] = request.META["CSRF_COOKIE"]
        self.assertEqual(LocalPreviewLoginView.as_view()(request).status_code, 200)

    def test_preview_tokens_cannot_authenticate_or_refresh_outside_local_development(self):
        tokens = self.login().data
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION="Bearer " + tokens["access"])
        self.assertEqual(client.get("/api/v1/auth/me/", HTTP_HOST="localhost").status_code, 200)
        with override_settings(DEBUG=False):
            self.assertEqual(client.get("/api/v1/auth/me/", HTTP_HOST="localhost").status_code, 401)
            self.assertEqual(client.post("/api/v1/auth/refresh/", {"refresh": tokens["refresh"]}, format="json", HTTP_HOST="localhost").status_code, 401)
        self.assertEqual(client.get("/api/v1/auth/me/", HTTP_HOST="example.test").status_code, 401)
