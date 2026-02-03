"""
Seed user accounts for the application.

Usage:
    uv run python manage.py seed_users

Creates:
- superadmin@app.local (Prod and Dev)
- developer@app.local (Dev only)
- contentmanager@app.local (Dev only)
- alicendlovu@app.local (Dev only)
"""

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from rolepermissions.roles import assign_role
from allauth.account.models import EmailAddress

User = get_user_model()


class Command(BaseCommand):
    help = "Seed user accounts for the application"

    # Default password for seeded users (should be changed on first login)
    DEFAULT_PASSWORD = "changeme123!"

    # Users to create in all environments
    PROD_USERS = [
        {
            "email": "superadmin@app.local",
            "username": "superadmin",
            "first_name": "Super",
            "last_name": "Admin",
            "role": "super_admin",
            "is_staff": True,
            "is_superuser": True,
        },
        {
            "email": "admin@app.local",
            "username": "admin",
            "first_name": "Admin",
            "last_name": "User",
            "role": "admin",
            "is_staff": True,
            "is_superuser": False,
        },
    ]

    # Additional users for development only
    DEV_USERS = [
        {
            "email": "developer@app.local",
            "username": "developer",
            "first_name": "Dev",
            "last_name": "User",
            "role": "developer",
            "is_staff": False,
            "is_superuser": False,
        },
        {
            "email": "contentmanager@app.local",
            "username": "contentmanager",
            "first_name": "Content",
            "last_name": "Manager",
            "role": "content_manager",
            "is_staff": True,
            "is_superuser": False,
        },
        {
            "email": "alicendlovu@app.local",
            "username": "alicendlovu",
            "first_name": "Alice",
            "last_name": "Ndlovu",
            "role": "user",
            "is_staff": False,
            "is_superuser": False,
        },
    ]

    def handle(self, *args, **options):
        self.stdout.write("Seeding users...")

        # Always create prod users
        for user_data in self.PROD_USERS:
            self._create_user(user_data)

        # Only create dev users if DEBUG is True
        if settings.DEBUG:
            self.stdout.write(
                self.style.WARNING("\n  [DEV MODE] Creating development users...")
            )
            for user_data in self.DEV_USERS:
                self._create_user(user_data)
        else:
            self.stdout.write(
                self.style.NOTICE("\n  [PROD MODE] Skipping development-only users.")
            )

        self.stdout.write(self.style.SUCCESS("\nDone!"))

    def _create_user(self, user_data: dict):
        email = user_data["email"]
        role = user_data.pop("role")

        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                "username": user_data["username"],
                "first_name": user_data["first_name"],
                "last_name": user_data["last_name"],
                "is_staff": user_data["is_staff"],
                "is_superuser": user_data["is_superuser"],
            },
        )

        if created:
            user.set_password(self.DEFAULT_PASSWORD)
            user.save()

            # Assign role
            assign_role(user, role)

            self.stdout.write(self.style.SUCCESS(f"  Created: {email} (role: {role})"))
        else:
            self.stdout.write(f"  Exists: {email}")

        # Bypass allauth email verification
        EmailAddress.objects.get_or_create(
            user=user, email=email, defaults={"verified": True, "primary": True}
        )
        # Ensure it's verified if it already existed
        EmailAddress.objects.filter(user=user, email=email).update(verified=True)

        # Re-add role to user_data for potential re-runs
        user_data["role"] = role
