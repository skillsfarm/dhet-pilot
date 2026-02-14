from django.core.management.base import BaseCommand
from django.utils import timezone

from apps.notifications.models import Notification
from django.contrib.auth import get_user_model


class Command(BaseCommand):
    help = "Seed notifications for alicendlovu"

    def handle(self, *args, **options):
        User = get_user_model()
        user = User.objects.filter(email="alicendlovu@app.local").first()
        if not user:
            self.stderr.write("User alicendlovu@app.local not found. Seed users first.")
            return

        notifications = [
            {
                "subject": "Welcome to DHET Scholarships",
                "message": "Explore available scholarships and funding opportunities tailored for you.",
                "status": "sent",
                "sent_at": timezone.now(),
            },
            {
                "subject": "New Learning Content Available",
                "message": "Check the content feed for new DHET guidance and resources.",
                "status": "sent",
                "sent_at": timezone.now(),
            },
        ]

        created_count = 0
        for payload in notifications:
            notification, created = Notification.objects.get_or_create(
                user=user,
                subject=payload["subject"],
                defaults={
                    "message": payload["message"],
                    "status": payload["status"],
                    "sent_at": payload["sent_at"],
                },
            )
            if not created:
                notification.message = payload["message"]
                notification.status = payload["status"]
                notification.sent_at = payload["sent_at"]
                notification.save()
            else:
                created_count += 1

        self.stdout.write(
            f"Seeded notifications for {user.email}. Created {created_count} new items."
        )
