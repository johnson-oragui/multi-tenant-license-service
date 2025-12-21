"""
Config Settings CI
"""

import os

from config.settings.base import *  # pylint: disable=wildcard-import, unused-wildcard-import

DEBUG = False

ALLOWED_HOSTS = ["*"]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

if os.environ.get("CI") != "true":
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": ":memory:",
        }
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.postgresql",
            "NAME": "license_service",
            "USER": "postgres",
            "PASSWORD": "postgres",
            "HOST": "localhost",
            "PORT": 5432,
        }
    }

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"
