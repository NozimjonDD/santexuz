"""The browser preview is available only to loopback development requests."""
from ipaddress import ip_address
from urllib.parse import urlsplit

from django.conf import settings


def local_preview_enabled(request):
    if not settings.DEBUG or not getattr(settings, "DEV_LOCAL_LOGIN", False):
        return False
    try:
        if urlsplit("//" + request.get_host()).hostname not in {"localhost", "127.0.0.1", "::1"}:
            return False
        address = ip_address(request.META.get("REMOTE_ADDR", ""))
    except ValueError:
        return False
    return address.is_loopback or bool(getattr(address, "ipv4_mapped", None) and address.ipv4_mapped.is_loopback)
