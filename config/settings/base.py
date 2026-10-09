from pathlib import Path
from typing import Any

from . import env

BASE_DIR = Path(__file__).resolve().parents[2]
SECRET_KEY = "foundation-test-only-key-not-for-production"
DEBUG = False
ALLOWED_HOSTS = ["localhost", "127.0.0.1", "testserver", "web"]
INSTALLED_APPS = [
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
]
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]
ROOT_URLCONF = "config.urls"
WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
            ]
        },
    }
]
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": env.str_value("POSTGRES_DB", "fitlink"),
        "USER": env.str_value("POSTGRES_USER", "fitlink"),
        "PASSWORD": env.str_value("POSTGRES_PASSWORD"),
        "HOST": env.str_value("POSTGRES_HOST", "127.0.0.1"),
        "PORT": env.int_value("POSTGRES_PORT", 5433, 1),
        "OPTIONS": {"connect_timeout": 2},
        "TEST": {"NAME": "test_fitlink"},
    }
}
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
LANGUAGE_CODE = "fa"
TIME_ZONE = "UTC"
USE_TZ = True
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = []
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = "Lax"
CSRF_COOKIE_SAMESITE = "Lax"
CSRF_FAILURE_VIEW = "config.api_security.csrf_failure"
STORAGE_BACKEND = env.str_value("STORAGE_BACKEND", "fake")
PROFILE_UPLOAD_MAX_BYTES = env.bounded_int(
    "PROFILE_UPLOAD_MAX_BYTES", 10_000_000, 10_000_000
)
PROFILE_UPLOAD_MAX_PENDING = env.bounded_int("PROFILE_UPLOAD_MAX_PENDING", 10, 10)
PROFILE_UPLOAD_DAILY_BYTES = env.bounded_int(
    "PROFILE_UPLOAD_DAILY_BYTES", 100_000_000, 100_000_000
)
PROFILE_UPLOAD_EXPIRY_SECONDS = env.bounded_int(
    "PROFILE_UPLOAD_EXPIRY_SECONDS", 3600, 3600
)
STORAGES: dict[str, dict[str, Any]] = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
LOG_LEVEL = env.str_value("LOG_LEVEL", "INFO")
if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    env.invalid("LOG_LEVEL")
RELEASE_ID = env.str_value("RELEASE_ID", "foundation")[:80]

INSTALLED_APPS += [
    "apps.accounts.apps.AccountsConfig",
    "apps.governance.apps.GovernanceConfig",
    "apps.assets.apps.AssetsConfig",
    "apps.athletes.apps.AthletesConfig",
    "apps.professionals.apps.ProfessionalsConfig",
]
AUTH_USER_MODEL = "accounts.User"

REDIS_URL = env.str_value("REDIS_URL", "redis://127.0.0.1:6380/0")
CELERY_BROKER_URL = env.str_value("CELERY_BROKER_URL", "redis://127.0.0.1:6380/1")
CELERY_RESULT_BACKEND = env.str_value(
    "CELERY_RESULT_BACKEND", "redis://127.0.0.1:6380/2"
)
OTP_RATE_REDIS_URL = env.str_value("OTP_RATE_REDIS_URL", "redis://127.0.0.1:6380/4")
CHANNEL_REDIS_URL = env.str_value("CHANNEL_REDIS_URL", "redis://127.0.0.1:6380/3")
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": REDIS_URL,
        "KEY_PREFIX": "fitlink",
        "OPTIONS": {"socket_connect_timeout": 2, "socket_timeout": 2},
    }
}

INSTALLED_APPS += ["rest_framework"]
REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "config.authentication.AccountSessionAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ["config.permissions.AccountActionPermission"],
}

CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = "UTC"
CELERY_ENABLE_UTC = True
CELERY_RESULT_EXPIRES = 86400
CELERY_TASK_ALWAYS_EAGER = False
CELERY_BEAT_SCHEDULE: dict[str, Any] = {
    "c02-outbox-scan": {"task": "apps.governance.tasks.scan_pending", "schedule": 30.0},
}
CELERY_IMPORTS = ("config.tasks", "apps.governance.tasks")
ASSET_PROCESSING_ENABLED = env.bool_value("ASSET_PROCESSING_ENABLED", False)
ASSET_SCANNER_HOST = env.str_value("ASSET_SCANNER_HOST")
ASSET_SCANNER_PORT = env.bounded_int("ASSET_SCANNER_PORT", 3310, 65535)
if ASSET_PROCESSING_ENABLED and ASSET_SCANNER_HOST not in {
    "scanner",
    "127.0.0.1",
    "localhost",
}:
    env.invalid("ASSET_SCANNER_HOST")
CELERY_BROKER_CONNECTION_TIMEOUT = 2
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True
CELERY_BROKER_CONNECTION_MAX_RETRIES = 10
CELERY_BROKER_TRANSPORT_OPTIONS = {"socket_connect_timeout": 2, "socket_timeout": 2}
CELERY_REDIS_SOCKET_CONNECT_TIMEOUT = 2
CELERY_REDIS_SOCKET_TIMEOUT = 2
CELERY_TASK_SOFT_TIME_LIMIT = 20
CELERY_TASK_TIME_LIMIT = 30
CELERY_WORKER_HIJACK_ROOT_LOGGER = False
CELERY_WORKER_REDIRECT_STDOUTS = False

INSTALLED_APPS += ["channels"]
CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {"hosts": [CHANNEL_REDIS_URL], "prefix": "fitlink", "expiry": 30},
    }
}

S3_ENDPOINT_URL = env.str_value("S3_ENDPOINT_URL", "http://127.0.0.1:9000")
S3_BUCKET_NAME = env.str_value("S3_BUCKET_NAME", "fitlink-private")
S3_REGION = env.str_value("S3_REGION", "us-east-1")
S3_ACCESS_KEY_ID = env.str_value("S3_ACCESS_KEY_ID")
S3_SECRET_ACCESS_KEY = env.str_value("S3_SECRET_ACCESS_KEY")
S3_ADDRESSING_STYLE = env.str_value("S3_ADDRESSING_STYLE", "path")
if STORAGE_BACKEND == "s3":
    STORAGES["default"] = {
        "BACKEND": "storages.backends.s3.S3Storage",
        "OPTIONS": {
            "endpoint_url": S3_ENDPOINT_URL,
            "bucket_name": S3_BUCKET_NAME,
            "region_name": S3_REGION,
            "access_key": S3_ACCESS_KEY_ID,
            "secret_key": S3_SECRET_ACCESS_KEY,
            "signature_version": "s3v4",
            "addressing_style": S3_ADDRESSING_STYLE,
            "default_acl": None,
            "querystring_auth": True,
            "querystring_expire": 60,
        },
    }

STATICFILES_DIRS = [BASE_DIR / "static"]
MIDDLEWARE.insert(0, "config.middleware.RequestIdMiddleware")
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {"json": {"()": "config.logging.JsonFormatter"}},
    "handlers": {"console": {"class": "logging.StreamHandler", "formatter": "json"}},
    "root": {"handlers": ["console"], "level": LOG_LEVEL},
    "loggers": {
        "django": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "celery": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "uvicorn": {"handlers": ["console"], "level": LOG_LEVEL, "propagate": False},
        "uvicorn.error": {
            "handlers": ["console"],
            "level": LOG_LEVEL,
            "propagate": False,
        },
        "uvicorn.access": {"handlers": [], "propagate": False},
    },
}

# Account settings are loaded in the concrete overlay.

MIDDLEWARE.insert(
    MIDDLEWARE.index("django.contrib.auth.middleware.AuthenticationMiddleware") + 1,
    "config.account_middleware.AccountMiddleware",
)
MIDDLEWARE.insert(
    MIDDLEWARE.index("django.middleware.csrf.CsrfViewMiddleware"),
    "config.upload_ingress.UploadRequestLimit",
)
