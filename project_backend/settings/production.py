from .base import *

DEBUG = False
DEV_LOCAL_LOGIN = False
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
if not ALLOWED_HOSTS or "*" in ALLOWED_HOSTS:
    raise ImproperlyConfigured("Production requires explicit ALLOWED_HOSTS.")
if DATABASES["default"]["ENGINE"] != "django.db.backends.postgresql":
    raise ImproperlyConfigured("Production requires PostgreSQL for transactional row locks.")
if not TELEGRAM_BOT_TOKEN or len(TELEGRAM_WEBHOOK_SECRET) < 32:
    raise ImproperlyConfigured("Configure Telegram token and a webhook secret of at least 32 characters.")
