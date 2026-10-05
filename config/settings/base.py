from pathlib import Path

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
STORAGE_BACKEND = env.str_value("STORAGE_BACKEND", "fake")
STORAGES = {
    "default": {"BACKEND": "django.core.files.storage.InMemoryStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}
LOG_LEVEL = env.str_value("LOG_LEVEL", "INFO")
if LOG_LEVEL not in {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}:
    env.invalid("LOG_LEVEL")
RELEASE_ID = env.str_value("RELEASE_ID", "foundation")[:80]

INSTALLED_APPS += ["apps.accounts.apps.AccountsConfig"]
AUTH_USER_MODEL = "accounts.User"

REDIS_URL = env.str_value("REDIS_URL", "redis://127.0.0.1:6380/0")
CELERY_BROKER_URL = env.str_value("CELERY_BROKER_URL", "redis://127.0.0.1:6380/1")
CELERY_RESULT_BACKEND = env.str_value(
    "CELERY_RESULT_BACKEND", "redis://127.0.0.1:6380/2"
)
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
        "rest_framework.authentication.SessionAuthentication"
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
