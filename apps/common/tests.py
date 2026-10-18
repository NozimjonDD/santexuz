from types import SimpleNamespace
from unittest.mock import Mock, patch

from django.test import SimpleTestCase, override_settings
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
