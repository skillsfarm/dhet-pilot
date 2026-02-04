from django.core.management.base import BaseCommand
from cookie_consent.models import CookieGroup
from cookie_consent.cache import delete_cache
from dhet_app.cookies import get_cookie_config
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seeds supported cookie groups from configuration."

    def handle(self, *args, **options):
        groups = get_cookie_config()

        for group_data in groups:
            group, created = CookieGroup.objects.update_or_create(
                varname=group_data["varname"], defaults=group_data
            )
            if created:
                logger.info(f"Created cookie group: {group.name}")
            else:
                logger.debug(f"Updated cookie group: {group.name}")

        delete_cache()
        logger.info("Deleted cookie consent cache.")
