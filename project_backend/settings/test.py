import os

os.environ.setdefault("SECRET_KEY", "santex-isolated-test-key-only-never-for-production-2026")
from .base import *

# PostgreSQL by default, so workflow locks and database triggers are exercised.
# Explicit DB_ENGINE=sqlite is a fast, non-concurrency fallback on the other machine.
PASSWORD_HASHERS = ["django.contrib.auth.hashers.MD5PasswordHasher"]
REST_FRAMEWORK = {**REST_FRAMEWORK, "DEFAULT_THROTTLE_CLASSES": []}
TELEGRAM_BOT_TOKEN = "123:test-token"
TELEGRAM_WEBHOOK_SECRET = "test-webhook-secret-for-isolated-tests-only"

# Negative authorization/input tests intentionally return 4xx. Keep unexpected
# server errors visible without presenting expected rejections as test failures.
LOGGING = {
    **LOGGING,
    "loggers": {
        **LOGGING.get("loggers", {}),
        "django.request": {"handlers": ["console", "file"], "level": "ERROR", "propagate": False},
        "django.security.csrf": {"handlers": ["console", "file"], "level": "ERROR", "propagate": False},
    },
}
