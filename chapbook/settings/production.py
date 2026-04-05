from .base import *  # noqa
from .base import env

ADMINS = [("Edema Code", "edemacode@gmail.com")]

SECRET_KEY = env("DJANGO_SECRET_KEY")

DEBUG = False

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS")

# Railway terminates SSL at the proxy — required to avoid redirect loops
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# WhiteNoise — serve static files directly from gunicorn, no Nginx needed
MIDDLEWARE.insert(1, "whitenoise.middleware.WhiteNoiseMiddleware")
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# Allow banner images up to 10MB (AI-generated images can be 4-8MB)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10 * 1024 * 1024   # 10MB

# Cloudinary — persistent media storage (Railway filesystem is ephemeral)
CLOUDINARY_STORAGE = {
    "CLOUD_NAME": env("CLOUDINARY_CLOUD_NAME"),
    "API_KEY": env("CLOUDINARY_API_KEY"),
    "API_SECRET": env("CLOUDINARY_API_SECRET"),
}
DEFAULT_FILE_STORAGE = "cloudinary_storage.storage.MediaCloudinaryStorage"
INSTALLED_APPS += ["cloudinary_storage", "cloudinary"]

# Email — console backend until a Celery worker is deployed
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="edemacode@gmail.com")
DOMAIN = env("DOMAIN")
SITE_NAME = "Chapbook"

# Allow login without email verification until real SMTP is wired up
ACCOUNT_EMAIL_VERIFICATION = "optional"

# Redis from Railway plugin (injected as REDIS_URL)
CELERY_BROKER_URL = env("REDIS_URL")
CELERY_RESULT_BACKEND = CELERY_BROKER_URL

# CORS — add frontend origin when ready
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

# Disable django-elasticsearch-dsl's auto-registered post_save/post_delete
# signals — Bonsai uses OpenSearch which fails the ES product check, causing
# every article save to 500. Our own guarded signal in search/signals.py
# handles indexing safely with try/except.
ELASTICSEARCH_DSL_AUTOSYNC = False

# JWT cookies — SameSite=None required for cross-origin cookie auth (frontend on different domain).
# Secure=True is required whenever SameSite=None is used (browser enforces this).
REST_AUTH = {
    **REST_AUTH,  # type: ignore[name-defined]  # noqa: F821
    "JWT_AUTH_SAMESITE": "None",
    "JWT_AUTH_SECURE": True,
}
