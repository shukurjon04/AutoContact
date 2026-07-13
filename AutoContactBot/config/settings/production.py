"""Production settings."""
from .base import *  # noqa: F401, F403
from decouple import config

DEBUG = False

# ---------------------------------------------------------------------------
# Allow localhost for Docker internal healthcheck
# ---------------------------------------------------------------------------
ALLOWED_HOSTS.extend(["localhost", "127.0.0.1", "django", "bot.robotronix.uz", "www.bot.robotronix.uz"])

# ---------------------------------------------------------------------------
# CSRF & Security
# ---------------------------------------------------------------------------
CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="https://bot.robotronix.uz,https://www.bot.robotronix.uz",
    cast=lambda v: [s.strip() for s in v.split(",") if s.strip()]
)

# ---------------------------------------------------------------------------
# Security
# ---------------------------------------------------------------------------
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_SECONDS = 31536000  # 1 year
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
X_FRAME_OPTIONS = "DENY"
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_REDIRECT_EXEMPT = [r"^health/$"]

# ---------------------------------------------------------------------------
# CORS
# ---------------------------------------------------------------------------
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS", default="", cast=lambda v: [s.strip() for s in v.split(",") if s.strip()]
)
CORS_ALLOW_CREDENTIALS = True
