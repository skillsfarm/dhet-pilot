"""
Seed role groups for the application.

Usage:
    uv run python manage.py seed_roles
"""

from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand
import logging

logger = logging.getLogger(__name__)


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

        logger.info("Seeding roles...")

        for role_name in self.ROLES:
            group, created = Group.objects.get_or_create(name=role_name)
            if created:
                created_count += 1
                logger.info(f"Created role: {role_name}")
            else:
                existing_count += 1
                logger.debug(f"Role exists: {role_name}")

        logger.info(
            f"Done! Created {created_count} new roles, {existing_count} already existed."
        )
