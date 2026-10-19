import hashlib
import hmac
import json
import time
import uuid
from urllib.parse import parse_qsl

from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import AuthenticationFailed

from apps.common.audit import record
from apps.users.models import User


def validate_init_data(raw):
    if not settings.TELEGRAM_BOT_TOKEN:
        raise AuthenticationFailed("Telegram authentication is not configured.")
    try:
        pairs = parse_qsl(raw, keep_blank_values=True, strict_parsing=True, max_num_fields=32)
        values = dict(pairs)
        if len(pairs) != len(values):
            raise ValueError("Duplicate fields")
        supplied_hash = values.pop("hash")
        # Telegram's HMAC validation includes all supplied fields other than hash.
        data_check = "\n".join(f"{key}={value}" for key, value in sorted(values.items()))
        secret = hmac.new(b"WebAppData", settings.TELEGRAM_BOT_TOKEN.encode(), hashlib.sha256).digest()
        expected = hmac.new(secret, data_check.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(expected, supplied_hash):
            raise ValueError("Invalid signature")
        age = int(time.time()) - int(values["auth_date"])
        if age < -30 or age > settings.TELEGRAM_INIT_DATA_MAX_AGE:
            raise ValueError("Expired init data")
        data = json.loads(values["user"])
        if not isinstance(data, dict) or type(data.get("id")) is not int or not 0 < data["id"] < 2**63 or data.get("is_bot"):
            raise ValueError("Invalid Telegram user")
        return data
    except (ValueError, KeyError, TypeError, OverflowError) as exc:
        raise AuthenticationFailed("Invalid or expired Telegram init data.") from exc


def get_or_create_telegram_user(data, language="uz"):
    """Only trusted, validated Telegram identities may enter this boundary."""
    user, created = User.objects.get_or_create(
        telegram_id=data["id"],
        defaults={"username": f"tg_{data['id']}_{uuid.uuid4().hex}", "role": "customer", "language": language,
                  "first_name": str(data.get("first_name", ""))[:150],
                  "last_name": str(data.get("last_name", ""))[:150]},
    )
    if created:
        user.set_unusable_password()
        user.save(update_fields=["password"])
    return user


@transaction.atomic
def telegram_login(raw, language):
    data = validate_init_data(raw)
    user = get_or_create_telegram_user(data, language)
    if not user.is_active or user.is_deleted:
        raise AuthenticationFailed("Account is inactive.")
    record(user, "auth.telegram_login", user)
    return user
