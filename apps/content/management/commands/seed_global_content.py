from django.core.management.base import BaseCommand
from django.db import transaction

from apps.content.models import Occupation, OccupationMedia


class Command(BaseCommand):
    help = "Seed global content feed media items"

    def handle(self, *args, **options):
        self.stdout.write("Seeding global content feed media...")

        occupation = Occupation.objects.order_by("ofo_code").first()
        if not occupation:
            self.stderr.write("No occupations found. Seed OFO data first.")
            return

        with transaction.atomic():
            media_item, created = OccupationMedia.objects.get_or_create(
                occupation=occupation,
                title="Department of Higher Education & Training",
                defaults={
                    "description": "Department of higher education & training scholarships",
                    "media_type": OccupationMedia.MediaType.VIDEO,
                    "source_type": OccupationMedia.SourceType.REMOTE,
                    "embed_code": (
                        '<iframe width="560" height="315" '
                        'src="https://www.youtube.com/embed/s39-yAV9rP4?si=iFq93g9mweiocMCI" '
                        'title="YouTube video player" frameborder="0" '
                        'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                        'gyroscope; picture-in-picture; web-share" '
                        'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
                    ),
                    "is_global": True,
                    "is_active": True,
                    "order": 0,
                },
            )

            if not created:
                media_item.description = (
                    "Department of higher education & training scholarships"
                )
                media_item.media_type = OccupationMedia.MediaType.VIDEO
                media_item.source_type = OccupationMedia.SourceType.REMOTE
                media_item.embed_code = (
                    '<iframe width="560" height="315" '
                    'src="https://www.youtube.com/embed/s39-yAV9rP4?si=iFq93g9mweiocMCI" '
                    'title="YouTube video player" frameborder="0" '
                    'allow="accelerometer; autoplay; clipboard-write; encrypted-media; '
                    'gyroscope; picture-in-picture; web-share" '
                    'referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>'
                )
                media_item.is_global = True
                media_item.is_active = True
                media_item.order = 0
                media_item.save()

        self.stdout.write("Global content feed media seeded.")
