"""Keep API failures JSON, with private diagnostics in the server log only."""
import logging

from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import InterfaceError, OperationalError
from django.db.models.deletion import ProtectedError
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.views import exception_handler as drf_exception_handler, set_rollback


logger = logging.getLogger("django.request")


def exception_handler(exc, context):
    if isinstance(exc, DjangoValidationError):
        exc = ValidationError(exc.message_dict if hasattr(exc, "message_dict") else exc.messages)
    if isinstance(exc, ProtectedError):
        exc = ValidationError({"detail": "This record is referenced by existing business records."})
    response = drf_exception_handler(exc, context)
    if response is not None:
        # Preserve DRF validation fields, authentication headers and status codes.
        return response

    request = context.get("request")
    logger.error(
        "API failure: %s %s", getattr(request, "method", ""), getattr(request, "path", ""),
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    set_rollback()
    unavailable = isinstance(exc, (OperationalError, InterfaceError))
    response = Response(
        {"detail": "Service temporarily unavailable." if unavailable else "Unable to complete this request.",
         "code": "service_unavailable" if unavailable else "server_error"},
        status=503 if unavailable else 500,
    )
    response["Cache-Control"] = "no-store"
    return response
