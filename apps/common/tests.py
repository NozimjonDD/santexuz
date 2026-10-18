from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
from django.db import OperationalError
from django.urls import reverse
from rest_framework.exceptions import ValidationError

from apps.common.routing import travel_minutes


class RoutingTests(SimpleTestCase):
    def setUp(self):
        self.store = SimpleNamespace(latitude="40.5", longitude="72.3")
        self.order = SimpleNamespace(latitude="40.6", longitude="72.4")

    @override_settings(ROUTING_BASE_URL="")
    def test_missing_provider_fails_explicitly(self):
        with self.assertRaises(ValidationError):
            travel_minutes(self.store, self.order)

    @override_settings(ROUTING_BASE_URL="https://routing.example.test")
    def test_provider_duration_is_converted_and_bad_response_rejected(self):
        response = Mock()
        response.json.return_value = {"routes": [{"duration": 1201}]}
        with patch("apps.common.routing.requests.get", return_value=response) as get:
            self.assertEqual(travel_minutes(self.store, self.order), 21)
            self.assertIn("72.3,40.5;72.4,40.6", get.call_args.args[0])
        response.json.return_value = {"routes": [{"duration": float("nan")}]}
        with patch("apps.common.routing.requests.get", return_value=response), self.assertRaises(ValidationError):
            travel_minutes(self.store, self.order)


class HealthProbeTests(SimpleTestCase):
    def test_liveness_has_no_database_dependency_and_is_not_cached(self):
        response = self.client.get(reverse("common:health-live"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertEqual(self.client.post(reverse("common:health-live")).status_code, 405)

    def test_readiness_checks_database_and_cache(self):
        with patch("apps.common.health.connection") as connection, patch("apps.common.health.cache") as cache:
            response = self.client.get(reverse("common:health-ready"))
            connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with("SELECT 1")
            cache.get.assert_called_once_with("__readiness__")
        self.assertEqual(response.json(), {"status": "ok"})

    def test_readiness_failure_does_not_expose_database_details(self):
        for dependency in ("connection", "cache"):
            with self.subTest(dependency=dependency), patch("apps.common.health.connection") as connection, patch("apps.common.health.cache") as cache:
                if dependency == "connection":
                    connection.cursor.side_effect = OperationalError("private database password/host")
                else:
                    cache.get.side_effect = OperationalError("private database cache error")
                response = self.client.get(reverse("common:health-ready"))
                self.assertEqual(response.status_code, 503)
                self.assertEqual(response.json(), {"status": "unavailable"})
                self.assertEqual(response["Cache-Control"], "no-store")
