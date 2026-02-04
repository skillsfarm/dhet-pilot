from django.core.management.base import BaseCommand
from django.contrib.sites.models import Site
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Updates the Site name and domain from settings or arguments"

    def add_arguments(self, parser):
        parser.add_argument("--name", type=str, help="Site name")
        parser.add_argument("--domain", type=str, help="Site domain")

    def handle(self, *args, **options):
        name = options["name"] or getattr(settings, "SITE_NAME", "DHET")
        domain = options["domain"] or getattr(settings, "SITE_DOMAIN", "localhost:8000")

        site, created = Site.objects.get_or_create(id=getattr(settings, "SITE_ID", 1))

        old_name = site.name
        old_domain = site.domain

        site.name = name
        site.domain = domain
        site.save()

        if created:
            logger.info(f"Created Site: {name} ({domain})")
        else:
            logger.info(f"Updated Site: '{old_name}' -> '{name}'")
            logger.info(f"Updated Domain: '{old_domain}' -> '{domain}'")
