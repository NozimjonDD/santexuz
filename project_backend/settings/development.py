from .base import *

SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False

CSRF_COOKIE_NAME = "csrftoken"
CSRF_HEADER_NAME = "HTTP_X_CSRFTOKEN"

# CSRF_TRUSTED_ORIGINS = [
#     'https://www.e-store.uz',
#     'https://e-store.uz',
# ]
STATICFILES_DIRS = [
    BASE_DIR / "staticfiles",  # extra shared folder for development
]
