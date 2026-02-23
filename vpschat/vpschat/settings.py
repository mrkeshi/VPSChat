from pathlib import Path
import os
import environ

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment (.env) ---
env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, "change-me"),
    ALLOWED_HOSTS=(list, []),
    CSRF_TRUSTED_ORIGINS=(list, []),
    SITE_NAME=(str, "VPS Chat"),
    COOKIE_AGE=(int, 60 * 60 * 24 * 7),  # 7 days
    SAVE_MESSAGES_TO_DB=(bool, True),
    ENABLE_FILE_UPLOAD=(bool, True),
    MAX_UPLOAD_SIZE=(int, 10 * 1024 * 1024),  # 10MB
    ALLOWED_UPLOAD_TYPES=(list, ["image/jpeg", "image/png", "image/webp", "image/gif", "video/mp4", "application/pdf", "text/plain"]),
    PRODUCTION_MODE=(bool, False),
    DATABASE_URL=(str, f"sqlite:///{BASE_DIR/'db.sqlite3'}"),
    REDIS_URL=(str, "redis://127.0.0.1:6379/0"),
    MEDIA_ROOT=(str, str(BASE_DIR / "media")),
    MEDIA_URL=(str, "/media/"),
)
environ.Env.read_env(os.path.join(BASE_DIR, ".env"))

DEBUG = env("DEBUG")
SECRET_KEY = env("SECRET_KEY")
SITE_NAME = env("SITE_NAME")

ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["127.0.0.1", "localhost"])
CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])

COOKIE_AGE = env("COOKIE_AGE")
SAVE_MESSAGES_TO_DB = env("SAVE_MESSAGES_TO_DB")
ENABLE_FILE_UPLOAD = env("ENABLE_FILE_UPLOAD")
MAX_UPLOAD_SIZE = env("MAX_UPLOAD_SIZE")
ALLOWED_UPLOAD_TYPES = env.list("ALLOWED_UPLOAD_TYPES")

PRODUCTION_MODE = env("PRODUCTION_MODE")

# --- Applications ---
# IMPORTANT (Channels): having "daphne" installed and listed here makes
# `python manage.py runserver` serve the ASGI application (WebSocket works).
# Put it before "django.contrib.staticfiles" as recommended by Channels docs.
INSTALLED_APPS = [
    "daphne",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "channels",
    "chat.apps.ChatConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "vpschat.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "chat.context_processors.site_settings",
            ],
        },
    },
]

WSGI_APPLICATION = "vpschat.wsgi.application"
ASGI_APPLICATION = "vpschat.asgi.application"

# --- Database ---
# Uses DATABASE_URL (sqlite locally; postgres in production typically)
DATABASES = {"default": env.db("DATABASE_URL")}

# --- Password validation ---
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "fa-ir"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# --- Static & Media ---
STATIC_URL = "/static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# IMPORTANT (Dev vs Prod):
# Using Manifest storage in DEBUG often raises errors if collectstatic hasn't been run.
# We keep it for production, but use plain storage locally.
if DEBUG:
    STORAGES = {
        "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"}
    }
else:
    STORAGES = {
        "staticfiles": {"BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"}
    }

MEDIA_URL = env("MEDIA_URL")
MEDIA_ROOT = env("MEDIA_ROOT")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# --- Sessions ---
SESSION_COOKIE_AGE = COOKIE_AGE
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = False

# --- Channels / Redis ---
REDIS_URL = env("REDIS_URL")
if PRODUCTION_MODE:
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {"hosts": [REDIS_URL]},
        }
    }
else:
    # In-memory for local development (no Redis required)
    CHANNEL_LAYERS = {"default": {"BACKEND": "channels.layers.InMemoryChannelLayer"}}

# --- Security (production hardening) ---
if PRODUCTION_MODE:
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
    SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=False)  # set True behind HTTPS
    SESSION_COOKIE_SECURE = env.bool("SESSION_COOKIE_SECURE", default=True)
    CSRF_COOKIE_SECURE = env.bool("CSRF_COOKIE_SECURE", default=True)
    SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)
    SECURE_HSTS_INCLUDE_SUBDOMAINS = env.bool("SECURE_HSTS_INCLUDE_SUBDOMAINS", default=True)
    SECURE_HSTS_PRELOAD = env.bool("SECURE_HSTS_PRELOAD", default=True)
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = "same-origin"
    X_FRAME_OPTIONS = "DENY"

# --- Logging (simple) ---
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {"console": {"class": "logging.StreamHandler"}},
    "root": {"handlers": ["console"], "level": "INFO"},
}

BASE_DIR = Path(__file__).resolve().parent.parent

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
        "OPTIONS": {
            "location": str(MEDIA_ROOT),
            "base_url": MEDIA_URL,
        },
    },
    "staticfiles": {
        "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    },
}