from django_intmd.settings.base import *


logger = structlog.get_logger(__name__)

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

CACHE = {
    "default": {
        "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
        "LOCATION": "unique-snowflake",
    }
}

logger.info("Test mode", database=DATABASES["default"]["ENGINE"])
