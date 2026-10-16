import os
from datetime import timedelta
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY")

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.getenv("DEBUG")
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",")

DJANGO_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
]

MY_APPS = [
    'apps',
    'apps.users',
    'apps.common',
]

THIRD_PARTY_APPS = [
    'corsheaders',
    'rest_framework',
    'rest_framework_simplejwt',
    'django_filters',
    'drf_yasg',
]

INSTALLED_APPS = DJANGO_APPS + MY_APPS + THIRD_PARTY_APPS

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'project_backend.urls'
AUTH_USER_MODEL = "users.User"

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],

        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'project_backend.wsgi.application'

if os.environ.get("POSTGRES") == "TRUE":
    print(4444444444444448888)
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": os.environ.get("DB_NAME"),
            "USER": os.environ.get("DB_USER"),
            "PASSWORD": os.environ.get("DB_PASSWORD"),
            "HOST": os.environ.get("DB_HOST", default="localhost"),
            "PORT": os.environ.get("DB_PORT", default="5432"),
        }
    }

else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

REST_FRAMEWORK = {
    "DEFAULT_PARSER_CLASSES": [
        'rest_framework.parsers.JSONParser',
        'rest_framework.parsers.FormParser',
        'rest_framework.parsers.MultiPartParser'
    ],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        # "rest_framework.authentication.BasicAuthentication",
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.AllowAny",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "rest_framework.filters.SearchFilter",
        "rest_framework.filters.OrderingFilter",
        "django_filters.rest_framework.DjangoFilterBackend",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.LimitOffsetPagination",
    "PAGE_SIZE": 10,

    # # Custom exception handler
    # 'EXCEPTION_HANDLER': 'apps.api.v1.admin.common.exception_handler.custom_exception_handler',
}
# --------------------------------------------------------------------
LANGUAGE_CODE = 'uz'

TIME_ZONE = 'Asia/Tashkent'

USE_I18N = True

USE_TZ = True

# MODELTRANSLATION
gettext = lambda s: s  # noqa
LANGUAGES = (
    ('uz', gettext('Uzbek')),
    ('ru', gettext('Russian')),
    ('en', gettext('English')),
)
MODELTRANSLATION_DEFAULT_LANGUAGE = 'uz'
MODELTRANSLATION_LANGUAGES = ("uz", "ru", "en")
MODELTRANSLATION_PREPOPULATE_LANGUAGE = "uz"

LOCALE_PATHS = [
    BASE_DIR / 'locale',
]
# ---------------------------------------------------
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

STATIC_URL = '/static/'

STATIC_ROOT = BASE_DIR / "static"  # where collectstatic will dump everything for production

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

OTP_EXPIRATION_TIME = int(os.getenv("OTP_EXPIRATION_TIME", 300))  # Default to 5 minutes if not set

# CELERY Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'  # or your Redis URL
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = "Asia/Tashkent"

CELERY_TASK_TRACK_STARTED = True
CELERY_TASK_TIME_LIMIT = 30 * 60
CELERY_BACKEND = os.environ.get("CELERY_BACKEND_URL", default="redis://127.0.0.1:6379/0")
CELERY_BROWSER_URL = os.environ.get("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")

# auditlog
AUDITLOG_INCLUDE_ALL_MODELS = True

# CACHE
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": os.environ.get("CACHE_REDIS_URL", default="redis://127.0.0.1:6379/0"),
    }
}

# SIMPLE JWT
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=1),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=15),
    "ROTATE_REFRESH_TOKENS": False,
    "BLACKLIST_AFTER_ROTATION": False,
    "UPDATE_LAST_LOGIN": True,

    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,

    "TOKEN_OBTAIN_SERIALIZER": "rest_framework_simplejwt.serializers.TokenObtainPairSerializer",
    "TOKEN_REFRESH_SERIALIZER": "rest_framework_simplejwt.serializers.TokenRefreshSerializer",
}

# --------------------------------ERROR--DEBUG--LOGS-------------------------------------------
STORAGE_FOLDER = 'storage/logs/'
os.makedirs(STORAGE_FOLDER, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    'formatters': {
        'standard': {
            'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
        },
    },
    "handlers": {
        'console': {
            'class': 'logging.StreamHandler',
            # 'formatter': 'simple'
        },

        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.RotatingFileHandler',
            'filename': os.getenv('APP_LOG_PATH', 'storage/logs/app.log'),
            'maxBytes': 1024 * 1024 * 50,  # 50 MB
            'backupCount': 5,
            'formatter': 'standard',
        },
        # 'file_security': {
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename':  os.getenv('SECURITY_LOG_PATH', 'storage/logs/security.log'),
        #     'maxBytes': 20 * 1024 * 1024,
        #     'backupCount': 10,
        #     'formatter': 'json',
        # },
        # 'file_celery': {
        #     'class': 'logging.handlers.RotatingFileHandler',
        #     'filename':  os.getenv('CELERY_LOG_PATH', 'storage/logs/celery.log'),
        #     'maxBytes': 30 * 1024 * 1024,
        #     'backupCount': 5,
        #     'formatter': 'verbose',
        # }
    },
    # 'root': {
    #     'level': 'INFO',
    #     'handlers': ['console', 'file_application']
    # },
    "loggers": {
        "": {
            "handlers": ["console", "file"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "DEBUG"),
            'propagate': False,
        },
        "django": {
            "handlers": ["console", "file"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            'propagate': False,
        },
        # 'django.security': {
        #     'handlers': ['file_security'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
        # 'celery': {
        #     'handlers': ['console', 'file_celery'],
        #     'level': 'INFO',
        #     'propagate': False,
        # },
    },
}
