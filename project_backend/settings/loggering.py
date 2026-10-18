import os
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[2]
log_path = Path(os.getenv("APP_LOG_PATH", "storage/logs/app.log"))
if not log_path.is_absolute():
    log_path = BASE_DIR / log_path
log_path.parent.mkdir(parents=True, exist_ok=True)

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "standard": {
            "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        },
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "standard",
        },
        "file": {
            "class": "logging.handlers.RotatingFileHandler",
            "filename": str(log_path),
            "maxBytes": 50 * 1024 * 1024,
            "backupCount": 5,
            "encoding": "utf-8",
            "formatter": "standard",
        },
    },
    "root": {
        "handlers": ["console", "file"],
        "level": os.getenv("DJANGO_LOG_LEVEL", "INFO").upper(),
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO").upper(),
            "propagate": False,
        },
        "django.server": {
            "handlers": ["console", "file"],
            "level": "INFO",
            "propagate": False,
        },
    },
}