"""Small probes with no credentials, database metadata or personal data in output."""
from django.core.cache import cache
from django.db import DatabaseError, connection
from django.http import JsonResponse
from django.views.decorators.http import require_safe


def response(status, code=200):
    result = JsonResponse({"status": status}, status=code)
    result["Cache-Control"] = "no-store"
    return result


@require_safe
def live(request):
    return response("ok")


@require_safe
def ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        # Also detects a missing production DatabaseCache table.
        cache.get("__readiness__")
    except DatabaseError:
        return response("unavailable", 503)
    return response("ok")
