from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from decouple import config
from apps.notifications.services import create_and_send_notification
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


class Command(BaseCommand):
    help = "Sends a test notification to the configured NOTIFICATION_TEST_EMAIL."

    def add_arguments(self, parser):
        parser.add_argument(
            "--no-cleanup",
            action="store_true",
            help="Skip cleanup of test data (user and notification records)",
        )

    def handle(self, *args, **options):
        test_email = config("NOTIFICATION_TEST_EMAIL", default=None)

        if not test_email:
            logger.error("NOTIFICATION_TEST_EMAIL is not set in .env")
            return

        logger.info(f"Preparing to send test notification to: {test_email}")

        # Get or create a user for this email
        user, created = User.objects.get_or_create(
            email=test_email,
            defaults={"username": test_email.split("@")[0], "is_active": True},
        )

        if created:
            user.set_unusable_password()
            user.save()
            logger.info(f"Created temporary user for {test_email}")

        subject = "Test Notification System"
        message = "This is a test notification from the DHET system to verify email configuration."

        success, notification = create_and_send_notification(user, subject, message)

        if success:
            logger.info(f"Successfully sent notification. Log ID: {notification.id}")
        else:
            logger.error(
                f"Failed to send notification. Error: {notification.error_message}"
            )

        if not options["no_cleanup"]:
            logger.info("Cleaning up test data...")

            # Clean up notification (logs cascade delete)
            notification.delete()
            logger.warning(f"Deleted test notification: {notification.id}")

            # Clean up user only if we created it
            if created:
                user.delete()
                logger.warning(f"Deleted temporary user: {user.username}")
            else:
                logger.info("Skipping user deletion (user existed before test)")
        else:
            logger.info("Skipping cleanup (--no-cleanup flag used)")
