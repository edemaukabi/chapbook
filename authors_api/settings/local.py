from .base import * #noqa
from .base import env

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env("DJANGO_SECRET_KEY", default="V-NBBD5xYaMjC7Gt3XWmdjS5Txtex-eUoBrJ5GJ1UPUHRWiYXi8",)

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

CSRF_TRUSTED_ORIGINS = ["http://localhost:8080"]
