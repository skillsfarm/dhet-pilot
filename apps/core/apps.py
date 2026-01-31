from django.apps import AppConfig


class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.core"
    label = "core"

    def ready(self):
        from django.apps import apps
        try:
            cookie_consent_app = apps.get_app_config('cookie_consent')
            cookie_consent_app.verbose_name = 'Cookie Consent'
            
            # Also fix model capitalization
            from cookie_consent.models import LogItem
            LogItem._meta.verbose_name = 'Log Item'
            LogItem._meta.verbose_name_plural = 'Log Items'
        except (LookupError, ImportError):
            pass
