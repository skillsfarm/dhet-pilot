from django.conf import settings


def app_version(request):
    return {
        "APP_VERSION": getattr(settings, "SPECTACULAR_SETTINGS", {}).get(
            "VERSION", "1.0.0"
        ),
        "ACCOUNT_LOGIN_BY_CODE_ENABLED": getattr(
            settings, "ACCOUNT_LOGIN_BY_CODE_ENABLED", False
        ),
    }
