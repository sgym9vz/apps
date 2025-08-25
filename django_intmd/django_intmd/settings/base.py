import os
from functools import lru_cache
from pathlib import Path
from typing import Optional

import environ
import structlog

from django_intmd.settings.logger_config import LoggerConfig

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR = BASE_DIR.parent

LoggerConfig()
logger = structlog.get_logger(__name__)

# Load environment variables
env = environ.Env(
    DEBUG=(bool, False),
    APP_ENV=(str, "development"),
    DJANGO_SECRET_KEY=(str, "secret_key"),
)


@lru_cache()
def get_env_filename() -> Optional[str]:
    env_filename = os.path.join(PROJECT_DIR, ".env")
    if os.path.exists(env_filename):
        return env_filename
    return None


env_filename = get_env_filename()

if env_filename is None:
    env = environ.Env(APP_ENV=(str, "production"))
else:
    environ.Env.read_env(env_filename)
    DEBUG = env("DEBUG")

logger.info("Environment", APP_ENV=env("APP_ENV"), DEBUG=DEBUG)

SECRET_KEY: str = env("DJANGO_SECRET_KEY")

ALLOWED_HOSTS = []


# Application definition
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "matching_app",
    "corsheaders",
]

MIDDLEWARE = [
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "django_intmd.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "django_intmd.wsgi.application"  # Gunicorn
ASGI_APPLICATION = "django_intmd.asgi.application"  # Daphne

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(env("REDIS_HOST"), env("REDIS_PORT"))],
        },
    }
}

# Database
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.mysql",
        "NAME": env("DB_NAME"),
        "USER": env("DB_USER"),
        "PASSWORD": env("DB_PASS"),
        "HOST": env("DB_HOST"),
        "PORT": "3306",
    }
}


# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
LANGUAGE_CODE = "en-us"

TIME_ZONE = "UTC"

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
STATIC_URL = "static/"

MEDIA_URL = "media/"

STATIC_ROOT = BASE_DIR / "static"
MEDIA_ROOT = STATIC_ROOT / "media"

# Default primary key field type
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# django-structlog configuration
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "structlog": {
            "()": structlog.stdlib.ProcessorFormatter,
            "processor": structlog.processors.JSONRenderer(),
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "structlog",
        },
    },
    "loggers": {
        "django_structlog": {
            "handlers": ["console"],
            "level": "INFO",
        },
        "django_intmd": {
            "handlers": ["console"],
            "level": "INFO",
        },
    },
}

# Auth
AUTH_USER_MODEL = "matching_app.User"

LOGIN_URL = "login"

LOGIN_REDIRECT_URL = "user_home"

LOGOUT_REDIRECT_URL = "index"

# Email
if env("APP_ENV") == "production" or env("APP_ENV") == "staging":
    EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
else:
    EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
logger.info(f"Using email backend: {EMAIL_BACKEND}")

EMAIL_HOST = env("EMAIL_HOST")
EMAIL_PORT = env("EMAIL_PORT")
EMAIL_USE_TLS = env("EMAIL_USE_TLS")
EMAIL_HOST_USER = env("EMAIL_HOST_USER")
EMAIL_HOST_PASSWORD = env("EMAIL_HOST_PASS")
EMAIL_DEFAULT_FROM = env("EMAIL_DEFAULT_FROM")

# CORS
if env("APP_ENV") == "development":
    CORS_ALLOWED_ORIGINS = [
        "http://localhost:8080",
    ]
else:
    CORS_ALLOWED_ORIGINS = []

# CSRF
if env("APP_ENV") == "development":
    CSRF_TRUSTED_ORIGINS = [
        "http://localhost:8080",
    ]
else:
    CSRF_TRUSTED_ORIGINS = []
