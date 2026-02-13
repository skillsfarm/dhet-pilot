from django.db import models
from simple_history.models import HistoricalRecords
from cuid2 import cuid_wrapper

# Initialize the CUID generator once
cuid_gen = cuid_wrapper()


def cuid_generator():
    """Generate a CUID for primary keys."""
    return cuid_gen()


class CuidModel(models.Model):
    """
    Abstract base model that uses CUIDs as primary keys.
    """

    id = models.CharField(
        primary_key=True, default=cuid_generator, max_length=30, editable=False
    )

    class Meta:
        abstract = True


class UserCookieConsent(CuidModel):
    """
    Logs cookie consent choices for authenticated users.
    """

    user = models.ForeignKey(
        "accounts.User", on_delete=models.CASCADE, related_name="cookie_consents"
    )
    group_varname = models.CharField(max_length=100)
    action = models.CharField(max_length=20)  # 'accepted' or 'declined'
    version = models.CharField(max_length=20, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "User Cookie Consent"
        verbose_name_plural = "User Cookie Consents"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.group_varname} ({self.action})"


class FeatureFlag(CuidModel):
    """
    Feature flag configuration stored in the database.
    Environment variables can override database settings.
    """

    key = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    is_enabled = models.BooleanField(default=True)
    history = HistoricalRecords()

    class Meta:
        verbose_name = "Feature Flag"
        verbose_name_plural = "Feature Flags"
        ordering = ["key"]

    def __str__(self):
        return f"{self.key} ({'enabled' if self.is_enabled else 'disabled'})"

    @classmethod
    def is_enabled_key(cls, key):
        from django.conf import settings

        overrides = getattr(settings, "FEATURE_FLAG_OVERRIDES", {})
        if key in overrides:
            return overrides[key]
        flag = cls.objects.filter(key=key).first()
        if flag is None:
            return True
        return flag.is_enabled

    @property
    def is_active(self):
        from django.conf import settings

        overrides = getattr(settings, "FEATURE_FLAG_OVERRIDES", {})
        if self.key in overrides:
            return overrides[self.key]
        return self.is_enabled
