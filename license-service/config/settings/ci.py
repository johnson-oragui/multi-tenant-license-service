"""
Config Settings CI
"""

from config.settings.base import *

DEBUG = False

ALLOWED_HOSTS = ["*"]

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]
