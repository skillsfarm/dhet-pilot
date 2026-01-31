from django.db import models
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
        "accounts.User",
        on_delete=models.CASCADE,
        related_name="cookie_consents"
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
