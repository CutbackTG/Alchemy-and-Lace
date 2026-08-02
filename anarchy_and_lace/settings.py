"""
Django settings for Anarchy & Lace.

Staging-first goals:
- Local dev: optional .env + SQLite + console email
- Heroku staging: env vars + DATABASE_URL (Postgres) + WhiteNoise static
- Minimal + reversible changes
"""

from __future__ import annotations

import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def env_bool(name: str, default: bool = False) -> bool:
    return os.environ.get(name, str(default)).strip().lower() in ("1", "true", "yes", "on")


def env_list(name: str, default: list[str] | None = None) -> list[str]:
    """
    Comma-separated env var -> list of stripped, non-empty values.
    """
    raw = os.environ.get(name, "")
    if not raw:
        return default or []
    return [x.strip() for x in raw.split(",") if x.strip()]


# Optional: load .env locally (safe on Heroku)
try:
    from dotenv import load_dotenv  # type: ignore

    load_dotenv()
except Exception:
    pass


# ---------------------------------------------------------
# Core
# ---------------------------------------------------------
SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-dev-only-change-me")
DEBUG = env_bool("DJANGO_DEBUG", False)


# ---------------------------------------------------------
# Hosts / Security
# ---------------------------------------------------------
# Heroku can route via randomized hostnames like:
# anarchy-and-lace-staging-<hash>.herokuapp.com
# so we allow the whole herokuapp.com domain in non-debug.
ALLOWED_HOSTS = ["anarchy-and-lace.herokuapp.com","localhost","127.0.0.1",'anarchy-and-lace-0b8e43b4f722.herokuapp.com']
ALLOWED_HOSTS += env_list("DJANGO_ALLOWED_HOSTS")
CORS_ALLOW_ALL_ORIGINS = True

# CSRF trusted origins (recommended for login/forms on custom domains)
# You can also set DJANGO_CSRF_TRUSTED_ORIGINS="https://example.com,https://www.example.com"
CSRF_TRUSTED_ORIGINS = env_list("DJANGO_CSRF_TRUSTED_ORIGINS", default=["https://*.herokuapp.com"])

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("DJANGO_SECURE_SSL_REDIRECT", True)
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True


# ---------------------------------------------------------
# Applications
# ---------------------------------------------------------
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.sites",
    "cloudinary",
    "cloudinary_storage",
    # Allauth
    "allauth",
    "allauth.account",
    "allauth.socialaccount",
    "allauth.socialaccount.providers.google",
    "allauth.socialaccount.providers.facebook",
    "allauth.socialaccount.providers.apple",
    # Local apps
    "home",
    "core",
    "catalog",
    "manager",
    "orders.apps.OrdersConfig",
    "reviews.apps.ReviewsConfig",
]


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",  # static files on Heroku
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "allauth.account.middleware.AccountMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]


# ---------------------------------------------------------
# URLs / Templates / WSGI
# ---------------------------------------------------------
ROOT_URLCONF = "anarchy_and_lace.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",  # allauth needs this
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                'anarchy_and_lace.context_processors.cart_count'
            ],
        },
    },
]

WSGI_APPLICATION = "anarchy_and_lace.wsgi.application"


# ---------------------------------------------------------
# Database
# ---------------------------------------------------------
DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    DATABASES = {
        "default": dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
        )
    }
    # Only require SSL options when using Postgres
    if DATABASE_URL.startswith("postgres"):
        DATABASES["default"].setdefault("OPTIONS", {})
        DATABASES["default"]["OPTIONS"]["sslmode"] = "require"
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }


# ---------------------------------------------------------
# Password validation
# ---------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]


# ---------------------------------------------------------
# Internationalization
# ---------------------------------------------------------
LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Europe/London"
USE_I18N = True
USE_TZ = True

# ---------------------------------------------------------
# Storages
# ---------------------------------------------------------
STORAGES = {
    "default": {
        "BACKEND": "cloudinary_storage.storage.MediaCloudinaryStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}


# ---------------------------------------------------------
# Static & Media
# ---------------------------------------------------------
STATIC_URL = "/static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STATICFILES_DIRS = [BASE_DIR / "static"]

# Media note:
# Heroku filesystem is ephemeral. MEDIA_* is fine locally,
# but use Cloudinary/S3 for real uploads.
MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"


# ---------------------------------------------------------
# Defaults
# ---------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


# ---------------------------------------------------------
# Sites / Auth / Allauth
# ---------------------------------------------------------
SITE_ID = int(os.environ.get("SITE_ID", "1"))

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

LOGIN_REDIRECT_URL = "/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"

# Allauth (new-style, avoids deprecated ACCOUNT_EMAIL_REQUIRED)
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = os.environ.get("ACCOUNT_EMAIL_VERIFICATION", "optional")

ACCOUNT_FORMS = {
    "signup": "core.forms.CustomerSignupForm",
}

SOCIALACCOUNT_PROVIDERS = {
    "google": {
        "APP": {
            "client_id": os.environ.get("GOOGLE_CLIENT_ID", ""),
            "secret": os.environ.get("GOOGLE_CLIENT_SECRET", ""),
            "key": "",
        }
    },
    "facebook": {
        "APP": {
            "client_id": os.environ.get("FACEBOOK_CLIENT_ID", ""),
            "secret": os.environ.get("FACEBOOK_CLIENT_SECRET", ""),
            "key": "",
        }
    },
    "apple": {
        "APP": {
            "client_id": os.environ.get("APPLE_CLIENT_ID", ""),
            "secret": os.environ.get("APPLE_CLIENT_SECRET", ""),
            "key": "",
        }
    },
}


# ---------------------------------------------------------
# Email
# ---------------------------------------------------------
EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.smtp.EmailBackend",
)

DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@anarchyandlace.local")
SERVER_EMAIL = DEFAULT_FROM_EMAIL

EMAIL_HOST = os.environ.get("EMAIL_HOST", "")
EMAIL_PORT = int(os.environ.get("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.environ.get("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.environ.get("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = env_bool("EMAIL_USE_TLS", True)


# ---------------------------------------------------------
# Stripe (placeholders)
# ---------------------------------------------------------
STRIPE_PUBLIC_KEY = os.environ.get("STRIPE_PUBLIC_KEY", "")
STRIPE_SECRET_KEY = os.environ.get("STRIPE_SECRET_KEY", "")
STRIPE_WEBHOOK_SECRET = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

STRIPE_SHIPPING_RATE_STANDARD = os.environ.get("STRIPE_SHIPPING_RATE_STANDARD", "")
STRIPE_SHIPPING_RATE_TRACKED24 = os.environ.get("STRIPE_SHIPPING_RATE_TRACKED24", "")

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'ERROR',
        },
    },
}

