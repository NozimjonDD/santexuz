from .base import *

# CORS HEADERS ---------------------------------------------
# CORS_ALLOW_ALL_ORIGINS = True # Allow all origins for CORS requests
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "https://frontend.example.com",
]
# CORS_ALLOW_CREDENTIALS = True  # Allow cookies to be included in CORS requests
# CORS_ALLOW_PRIVATE_NETWORK = True  # Allow private network requests
