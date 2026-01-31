from pathlib import Path

from decouple import config, Csv
from django.templatetags.static import static
import dj_database_url


TIME_ZONE = "Africa/Johannesburg"
USE_TZ = True

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY")
DEBUG = config("DEBUG", cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

INSTALLED_APPS = [
    "dhet_admin",  # admin theme
    "dhet_admin.contrib.import_export",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "whitenoise.runserver_nostatic",
    "django.contrib.staticfiles",
    "simple_history",
    "storages",
    "django.contrib.sites",  # allauth
    "allauth",
    "allauth.account",
    "rest_framework",
    "drf_spectacular",
    "rolepermissions",
    "cookie_consent",
    "apps.accounts",
    "apps.core",
    "apps.storage",
    "apps.notifications",
    "apps.content",
    "apps.candidates",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "simple_history.middleware.HistoryRequestMiddleware",
    "apps.core.middleware.RestrictedAdminMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

ROOT_URLCONF = "dhet_app.urls"
SITE_ID = 1
SITE_NAME = config("SITE_NAME", default="DHET")
SITE_DOMAIN = config("SITE_DOMAIN", default="localhost:8000")

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
                "dhet_app.context_processors.app_version",
            ],
        },
    },
]

DATABASES = {"default": dj_database_url.parse(config("DATABASE_URL", cast=str))}

STATIC_URL = "/staticfiles/"
STATICFILES_DIRS = [BASE_DIR / "theme" / "dist", BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

# ------------- Storage Configuration -------------
# Generic S3 / Object Storage credentials
ACCESS_KEY_ID = config("ACCESS_KEY_ID", default=None)
SECRET_ACCESS_KEY = config("SECRET_ACCESS_KEY", default=None)
STORAGE_BUCKET_NAME = config("STORAGE_BUCKET_NAME", default=None)
S3_ENDPOINT_URL = config("S3_ENDPOINT_URL", default=None)
S3_REGION_NAME = config("S3_REGION_NAME", default="nyc3")
S3_CUSTOM_DOMAIN = config("S3_CUSTOM_DOMAIN", default=None)

if ACCESS_KEY_ID and SECRET_ACCESS_KEY and STORAGE_BUCKET_NAME:
    STORAGES = {
        "default": {
            "BACKEND": "storages.backends.s3.S3Storage",
            "OPTIONS": {
                "access_key": ACCESS_KEY_ID,
                "secret_key": SECRET_ACCESS_KEY,
                "bucket_name": STORAGE_BUCKET_NAME,
                "endpoint_url": S3_ENDPOINT_URL,
                "region_name": S3_REGION_NAME,
                "default_acl": "public-read",
                "object_parameters": {
                    "CacheControl": "max-age=86400",
                },
                "location": "media",
            },
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }

    # Configure Media URL
    if S3_CUSTOM_DOMAIN:
        MEDIA_URL = f"https://{S3_CUSTOM_DOMAIN}/media/"
    elif S3_ENDPOINT_URL:
        # Path style: https://{endpoint}/{bucket}/media/
        MEDIA_URL = f"{S3_ENDPOINT_URL}/{STORAGE_BUCKET_NAME}/media/"
    else:
        # Standard S3 style
        MEDIA_URL = f"https://{STORAGE_BUCKET_NAME}.s3.amazonaws.com/media/"

else:
    # Local development storage
    STORAGES = {
        "default": {
            "BACKEND": "django.core.files.storage.FileSystemStorage",
        },
        "staticfiles": {
            "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
        },
    }
    MEDIA_URL = "/media/"
    MEDIA_ROOT = BASE_DIR / "media"

# ------------- allauth -------------
AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]
AUTH_USER_MODEL = "accounts.User"
ACCOUNT_EMAIL_VERIFICATION = config("ACCOUNT_EMAIL_VERIFICATION", default="mandatory")
ACCOUNT_LOGIN_METHODS = {"email"}
ACCOUNT_SIGNUP_FIELDS = ["email*", "password1*", "password2*"]
ACCOUNT_ADAPTER = "apps.accounts.adapter.AccountAdapter"
LOGIN_REDIRECT_URL = "/dashboard/"
ACCOUNT_LOGOUT_REDIRECT_URL = "/"
SOCIALACCOUNT_ENABLED = False
ACCOUNT_LOGIN_BY_CODE_ENABLED = True
ACCOUNT_EMAIL_SUBJECT_PREFIX = ""

# ------------- Email Configuration (Zoho Recommended) -------------
EMAIL_BACKEND = config(
    "EMAIL_BACKEND", default="django.core.mail.backends.smtp.EmailBackend"
)
EMAIL_HOST = config("EMAIL_HOST", default="smtp.zoho.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_USE_SSL = config("EMAIL_USE_SSL", default=False, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")
DEFAULT_FROM_EMAIL = config("DEFAULT_FROM_EMAIL", default="")

# ------------- DRF -------------
REST_FRAMEWORK = {
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework.authentication.SessionAuthentication",
        "rest_framework.authentication.TokenAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": ["rest_framework.permissions.IsAuthenticated"],
}
SPECTACULAR_SETTINGS = {
    "TITLE": "DHET API",
    "DESCRIPTION": "API documentation for DHET",
    "VERSION": "1.0.0",
    "SERVE_PERMISSIONS": ["rest_framework.permissions.AllowAny"],
    "SCHEMA_PATH_PREFIX": "/api/",
}

# ------------- rolepermissions -------------
ROLEPERMISSIONS_MODULE = "dhet_app.roles"

# ------------- Cookie Consent -------------
COOKIE_CONSENT_ENABLED = config("COOKIE_CONSENT_ENABLED", default=True, cast=bool)
COOKIE_CONSENT_LOG_ENABLED = False
COOKIE_CONSENT_CACHE_BACKEND = "default"
COOKIE_CONSENT_SUCCESS_URL = "/"
COOKIE_CONSENT_NAME = "cookie_consent_status"
COOKIE_CONSENT_HTTPONLY = False  # Allow JS to check if cookie is set

# Allow JS to read CSRF token
CSRF_COOKIE_HTTPONLY = False
