"""
Seed role groups for the application.

Usage:
    uv run python manage.py seed_roles
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Seed role groups for the application"

    # Add new roles here as needed
    ROLES = [
        "user",
        "developer",
        "content_manager",
        "admin",
        "super_admin",
    ]

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0

        for role_name in self.ROLES:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"  Created role: {role_name}"))
            else:
                existing_count += 1
                self.stdout.write(f"  Role exists: {role_name}")

        self.stdout.write("")
        self.stdout.write(
            self.style.SUCCESS(
                f"Done! Created {created_count} new roles, {existing_count} already existed."
            )
        )
