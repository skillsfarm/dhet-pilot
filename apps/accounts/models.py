from django.conf import settings
from simple_history.models import HistoricalRecords
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.contrib.auth.models import AbstractUser
from apps.core.models import CuidModel


class User(AbstractUser, CuidModel):
    """
    Custom User model with CUID primary key.
    """

    pass

    history = HistoricalRecords()


class UserProfile(models.Model):
    """
    Extended user profile with onboarding tracking.
    Only used for 'user' and 'developer' roles.
    """

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="profile",
    )
    is_onboarded = models.BooleanField(default=False)
    onboarding_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    history = HistoricalRecords()

    def __str__(self):
        return f"{self.user.username}'s profile"
