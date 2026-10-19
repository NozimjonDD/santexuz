from urllib.parse import urlsplit

from .base import *

DEBUG = False
DEV_LOCAL_LOGIN = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REFERRER_POLICY = "strict-origin-when-cross-origin"
REST_FRAMEWORK = {**REST_FRAMEWORK, "NUM_PROXIES": 1}
DATABASES["default"]["CONN_HEALTH_CHECKS"] = True
FILE_UPLOAD_PERMISSIONS = 0o600
FILE_UPLOAD_DIRECTORY_PERMISSIONS = 0o700
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
        "OPTIONS": {"file_permissions_mode": 0o644, "directory_permissions_mode": 0o755},
    },
}
# Shared throttling/cache state across Gunicorn processes, without another daemon.
CACHES = {"default": {
    "BACKEND": "django.core.cache.backends.db.DatabaseCache",
    "LOCATION": "santex_cache", "KEY_PREFIX": "santex",
    "TIMEOUT": 300, "OPTIONS": {"MAX_ENTRIES": 20000},
}}
# Each process writes to stderr; systemd/journald handles collection and rotation.
# A shared RotatingFileHandler is unsafe across multiple Gunicorn workers.
LOGGING = {
    **LOGGING,
    "handlers": {"console": LOGGING["handlers"]["console"]},
    "root": {**LOGGING["root"], "handlers": ["console"]},
    "loggers": {
        name: {**config, "handlers": ["console"]}
        for name, config in LOGGING["loggers"].items()
    },
}
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Production requires explicit ALLOWED_HOSTS.")
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("Production requires PostgreSQL for transactional row locks.")
if not TELEGRAM_BOT_TOKEN or TELEGRAM_BOT_TOKEN.startswith("CHANGE_ME") or len(TELEGRAM_WEBHOOK_SECRET) < 32:
    raise ImproperlyConfigured("Configure Telegram token and a webhook secret of at least 32 characters.")
if len(SECRET_KEY) < 50 or len(set(SECRET_KEY)) < 5:
    raise ImproperlyConfigured("Production requires a random SECRET_KEY of at least 50 characters.")
if not DATABASES["default"]["PASSWORD"] or DATABASES["default"]["PASSWORD"].startswith("CHANGE_ME"):
    raise ImproperlyConfigured("Configure a production database password.")
mini_app = urlsplit(MINI_APP_URL)
if mini_app.scheme != "https" or not mini_app.hostname or mini_app.username or mini_app.password:
    raise ImproperlyConfigured("MINI_APP_URL must be an HTTPS URL.")
if mini_app.hostname not in ALLOWED_HOSTS:
    raise ImproperlyConfigured("The Mini App hostname must appear explicitly in ALLOWED_HOSTS.")
routing = urlsplit(ROUTING_BASE_URL)
if routing.scheme not in {"http", "https"} or not routing.hostname or routing.username or routing.password:
    raise ImproperlyConfigured("Configure an OSRM-compatible ROUTING_BASE_URL before production startup.")
if not CONTRACT_FONT_PATH or not Path(CONTRACT_FONT_PATH).is_file():
    raise ImproperlyConfigured("Configure an existing Unicode TTF file in CONTRACT_FONT_PATH.")
