import math
import requests
from django.conf import settings
from rest_framework.exceptions import ValidationError


def travel_minutes(store, order):
    """OSRM-compatible routing adapter. Never substitute a fabricated duration."""
    base = settings.ROUTING_BASE_URL.rstrip("/")
    if not base:
        raise ValidationError({"routing": "Routing provider is not configured."})
    if store.latitude is None or store.longitude is None:
        raise ValidationError({"routing": "Store coordinates are required."})
    coordinates = f"{store.longitude},{store.latitude};{order.longitude},{order.latitude}"
    headers = {"Authorization": f"Bearer {settings.ROUTING_API_KEY}"} if settings.ROUTING_API_KEY else {}
    try:
        response = requests.get(f"{base}/route/v1/driving/{coordinates}", params={"overview": "false"}, headers=headers, timeout=10)
        response.raise_for_status()
        duration = float(response.json()["routes"][0]["duration"])
        if not math.isfinite(duration) or duration < 0:
            raise ValueError("Invalid route duration")
        return max(1, math.ceil(duration / 60))
    except (requests.RequestException, ValueError, KeyError, IndexError, TypeError):
        raise ValidationError({"routing": "Routing provider unavailable. Retry later."}) from None
