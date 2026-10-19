"""Execute on the verification machine; no live services are required."""
from django.core.exceptions import ValidationError as ModelValidationError
from django.db import OperationalError
from django.test import SimpleTestCase
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.test import APIRequestFactory
from rest_framework.views import APIView

from apps.common.exception_handler import exception_handler


class FailingView(APIView):
    authentication_classes = ()
    permission_classes = (permissions.AllowAny,)
    throttle_classes = ()
    failure = None

    def get(self, request):
        raise self.failure


class APIErrorTests(SimpleTestCase):
    def response(self, failure):
        request = APIRequestFactory().get("/api/v1/common/services/", HTTP_ACCEPT="application/json")
        with self.assertLogs("django.request", level="ERROR"):
            response = FailingView.as_view(failure=failure)(request)
        response.render()
        self.assertEqual(response["Content-Type"], "application/json")
        self.assertEqual(response["Cache-Control"], "no-store")
        self.assertNotIn(b"private-password", response.content)
        return response

    def test_database_connection_failure_is_json_503_without_private_details(self):
        response = self.response(OperationalError("private-password / database host"))
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.data["code"], "service_unavailable")

    def test_unexpected_failure_is_json_500_without_traceback(self):
        response = self.response(RuntimeError("private-password / internal trace"))
        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.data["code"], "server_error")

    def test_model_validation_becomes_400_and_drf_field_shapes_stay_intact(self):
        for error in (ModelValidationError({"address": ["Required"]}), ValidationError({"address": ["Required"]})):
            with self.subTest(error=type(error).__name__):
                response = exception_handler(error, {})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.data, {"address": ["Required"]})
