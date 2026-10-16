import secrets

from django.conf import settings


def generate_otp(digits=4) -> str:
    if settings.SMS_DEBUG:
        return "0000"

    num = secrets.randbelow(10 ** digits)
    return f"{num:0{digits}d}"


def generate_secret(length=40) -> str:
    return secrets.token_hex(length // 2)
