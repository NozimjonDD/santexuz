import os
from datetime import timedelta
from pathlib import Path

from django.core.exceptions import ImproperlyConfigured
from dotenv import load_dotenv

from .loggering import LOGGING

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env", override=False)


def env_list(name, default=""):
    return [value.strip() for value in os.getenv(name, default).split(",") if value.strip()]


SECRET_KEY = os.getenv("SECRET_KEY", "")
if not SECRET_KEY or SECRET_KEY.startswith("CHANGE_ME"):
    raise ImproperlyConfigured("Set a unique SECRET_KEY in .env before starting Django.")
DEBUG = False
DEV_LOCAL_LOGIN = False
ALLOWED_HOSTS = env_list("ALLOWED_HOSTS", "localhost,127.0.0.1")

DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MY_APPS = ["apps.common",
           "apps.users",
           "apps.catalog",
           "apps.orders",
           "apps.tg_bot"
           ]

THIRD_PARTY_APPS = [
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt.token_blacklist",
    "django_filters",
    "drf_spectacular",
]
INSTALLED_APPS = DJANGO_APPS + MY_APPS + THIRD_PARTY_APPS
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware", "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware", "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware", "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware", "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "middleware.security.PrivateAPICacheMiddleware",
]
ROOT_URLCONF = "project_backend.urls"
AUTH_USER_MODEL = "users.User"
AUTHENTICATION_BACKENDS = ["apps.common.authentication.ActiveUserBackend"]
TEMPLATES = [{
    "BACKEND": "django.template.backends.django.DjangoTemplates",
    "DIRS": [BASE_DIR / "templates"], "APP_DIRS": True,
    "OPTIONS": {"context_processors": [
        "django.template.context_processors.request", "django.contrib.auth.context_processors.auth",
        "django.contrib.messages.context_processors.messages",
    ]},
}]

WSGI_APPLICATION = "project_backend.wsgi.application"
ASGI_APPLICATION = "project_backend.asgi.application"

if os.getenv("DB_ENGINE", "postgresql") == "sqlite":
    DATABASES = {"default": {"ENGINE": "django.db.backends.sqlite3", "NAME": BASE_DIR / "db.sqlite3"}}
else:
    DATABASES = {"default": {
        "ENGINE": "django.db.backends.postgresql", "NAME": os.getenv("DB_NAME", "santex"),
        "USER": os.getenv("DB_USER", "santex"), "PASSWORD": os.getenv("DB_PASSWORD", ""),
        "HOST": os.getenv("DB_HOST", "127.0.0.1"), "PORT": os.getenv("DB_PORT", "5432"),
        "CONN_MAX_AGE": 60, "OPTIONS": {"sslmode": os.getenv("DB_SSLMODE", "prefer")},
    }}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator", "OPTIONS": {"min_length": 12}},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ["apps.common.authentication.ApplicationJWTAuthentication"],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend",
                                "rest_framework.filters.SearchFilter"],
    "DEFAULT_PAGINATION_CLASS": "apps.common.pagination.StandardPagination", "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "EXCEPTION_HANDLER": "apps.common.exception_handler.exception_handler",
    "DEFAULT_THROTTLE_CLASSES": ["rest_framework.throttling.AnonRateThrottle",
                                 "rest_framework.throttling.UserRateThrottle"],
    "DEFAULT_THROTTLE_RATES": {"anon": "60/min", "user": "300/min", "login": "10/min"},
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=15), "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True, "BLACKLIST_AFTER_ROTATION": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "CHECK_REVOKE_TOKEN": True,
    "TOKEN_REFRESH_SERIALIZER": "apps.api.v1.auth.serializers.ApplicationTokenRefreshSerializer",
    "USER_AUTHENTICATION_RULE": "apps.common.authentication.active_user_rule",
}

SPECTACULAR_SETTINGS = {"TITLE": "Santex API", "VERSION": "1.0.0", "SERVE_INCLUDE_SCHEMA": False,
                        "SERVE_PERMISSIONS": ["rest_framework.permissions.IsAdminUser"],
                        "ENUM_NAME_OVERRIDES": {
                            "AccountLanguage": "apps.catalog.models.LANGUAGES",
                            "LoginLanguage": ["uz", "ru", "en"],
                            "OrderStatus": "apps.orders.models.Order.Status",
                            "DeliveryStatus": "apps.orders.models.Delivery.Status",
                            "DeliveryUpdateStatus": ["preparing", "dispatched", "delivered"],
                        }}
LANGUAGE_CODE = "uz"
LANGUAGES = [("uz", "O‘zbek"), ("ru", "Русский"), ("en", "English")]
TIME_ZONE = "Asia/Tashkent"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"
STATIC_ROOT = Path(os.getenv("STATIC_ROOT", str(BASE_DIR / "staticfiles")))
STATICFILES_DIRS = [BASE_DIR / "static"]
# Private media must only be streamed by authenticated API views, never by nginx aliases.
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "storage" / "private")))
MEDIA_URL = "/private-media/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

CORS_ALLOWED_ORIGINS = env_list("CORS_ALLOWED_ORIGINS")
CSRF_TRUSTED_ORIGINS = env_list("CSRF_TRUSTED_ORIGINS")
CORS_ALLOW_CREDENTIALS = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True
X_FRAME_OPTIONS = "SAMEORIGIN"
SECURE_CONTENT_TYPE_NOSNIFF = True
DATA_UPLOAD_MAX_MEMORY_SIZE = 5 * 1024 * 1024
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024
MAX_ORDER_MEDIA_BYTES = int(os.getenv("MAX_ORDER_MEDIA_BYTES", "20971520"))

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_BOT_USERNAME = os.getenv("TELEGRAM_BOT_USERNAME", "")
TELEGRAM_WEBHOOK_SECRET = os.getenv("TELEGRAM_WEBHOOK_SECRET", "")
TELEGRAM_INIT_DATA_MAX_AGE = int(os.getenv("TELEGRAM_INIT_DATA_MAX_AGE", "300"))

MINI_APP_URL = os.getenv("MINI_APP_URL", "")
ROUTING_BASE_URL = os.getenv("ROUTING_BASE_URL", "")
ROUTING_API_KEY = os.getenv("ROUTING_API_KEY", "")
CONTRACT_FONT_PATH = os.getenv("CONTRACT_FONT_PATH", "")
