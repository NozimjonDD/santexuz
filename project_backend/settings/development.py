from .base import *

DEBUG = True
DEV_LOCAL_LOGIN = os.getenv("DEV_LOCAL_LOGIN", "true").lower() in ("1", "true", "yes", "on")
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
