from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from rolepermissions.roles import assign_role

from .models import UserProfile

User = get_user_model()


@receiver(post_save, sender=User)
def assign_default_user_role(sender, instance, created, **kwargs):
    """
    Automatically assign the 'user' role to newly created users
    who don't have any role assigned.
    """
    if created and not instance.groups.exists():
        # Only assign if the user has no groups/roles yet
        # This handles both direct user creation and allauth signup
        assign_role(instance, "user")


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Create a UserProfile for new users automatically.
    This is used to track onboarding status.
    """
    if created:
        UserProfile.objects.get_or_create(user=instance)
